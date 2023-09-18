from collections import deque
from copy import deepcopy

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Categorical
from tqdm import tqdm


class Config:
    def __init__(self) -> None:
        # self.env_name = "CartPole-v1"  # 环境名字
        self.env_name = "2048-v0"  # 环境名字
        self.mode = "train"  # train or test
        self.seed = 1  # 随机种子
        self.device = "cuda"  # device to use
        self.train_eps = 10000  # 训练的回合数
        self.test_eps = 20  # 测试的回合数
        self.max_steps = 500  # 每个回合的最大步数
        self.eval_eps = 5  # 评估的回合数
        self.eval_per_episode = 50  # 评估的频率

        self.gamma = 0.95  # 折扣因子
        self.k_epochs = 50  # 更新策略网络的次数
        self.actor_lr = 3e-4  # actor网络的学习率
        self.critic_lr = 3e-4  # critic网络的学习率
        self.eps_clip = 0.2  # epsilon-clip
        self.entropy_coef = 0.01  # entropy的系数
        self.update_freq = 500 * 8  # 更新频率
        self.actor_hidden_dim = 16  # actor网络的隐藏层维度
        self.actor_num_heads = 2
        self.actor_num_layers = 4
        self.critic_hidden_dim = 16  # critic网络的隐藏层维度
        self.critic_num_heads = 4
        self.critic_num_layers = 2

        self.num_actions = 4
        self.num_states = None


class ActorSoftmax(nn.Module):
    def __init__(
        self, input_dim, output_dim, hidden_dim=256, num_heads=4, num_layers=2
    ):
        super().__init__()
        self.emb = nn.Embedding(input_dim + 1, hidden_dim)
        self.pos_emb = nn.Parameter(torch.randn(input_dim + 1, hidden_dim) * 0.01)
        self.transformer = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(d_model=hidden_dim, nhead=num_heads),
            num_layers=num_layers,
        )
        self.postprocess = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, x: torch.Tensor):
        x = x + 1
        x = torch.cat([x.new_zeros((x.shape[0], 1)), x], dim=-1)
        x = self.emb(x) + self.pos_emb.unsqueeze(0)
        x = self.transformer(x.permute(1,0,2)).permute(1,0,2)
        x = x[:, 0, :]
        x = self.postprocess(x)
        probs = F.softmax(x, dim=-1)
        return probs


class Critic(nn.Module):
    def __init__(
        self, input_dim, hidden_dim=256, num_heads=4, num_layers=2
    ):
        super().__init__()
        self.emb = nn.Embedding(input_dim + 1, hidden_dim)
        self.pos_emb = nn.Parameter(torch.randn(input_dim + 1, hidden_dim) * 0.01)
        self.transformer = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(d_model=hidden_dim, nhead=num_heads),
            num_layers=num_layers,
        )
        self.postprocess = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, x: torch.Tensor):
        x = x + 1
        x = torch.cat([x.new_zeros((x.shape[0], 1)), x], dim=-1)
        x = self.emb(x) + self.pos_emb.unsqueeze(0)
        x = self.transformer(x.permute(1,0,2)).permute(1,0,2)
        x = x[:, 0, :]
        x = self.postprocess(x).squeeze(-1)
        return x


class PGReplay:
    def __init__(self):
        self.buffer = deque()

    def sample(self):
        '''sample all the transitions'''
        batch = list(self.buffer)
        return zip(*batch)

    def push(self, transitions):
        '''_summary_
        Args:
            trainsitions (tuple): _description_
        '''
        self.buffer.append(transitions)

    def clear(self):
        self.buffer.clear()

    def __len__(self):
        return len(self.buffer)


class Agent:
    def __init__(self, cfg: Config) -> None:
        self.gamma = cfg.gamma
        self.device = torch.device(cfg.device)
        self.actor = ActorSoftmax(
            cfg.num_states,
            cfg.num_actions,
            hidden_dim=cfg.actor_hidden_dim,
            num_heads=cfg.actor_num_heads,
            num_layers=cfg.actor_num_layers,
        ).to(self.device)
        self.critic = Critic(
            cfg.num_states,
            hidden_dim=cfg.critic_hidden_dim,
            num_heads=cfg.critic_num_heads,
            num_layers=cfg.critic_num_layers,
        ).to(self.device)
        self.actor_optimizer = torch.optim.Adam(
            self.actor.parameters(), lr=cfg.actor_lr
        )
        self.critic_optimizer = torch.optim.Adam(
            self.critic.parameters(), lr=cfg.critic_lr
        )
        self.memory = PGReplay()
        self.k_epochs = cfg.k_epochs  # update policy for K epochs
        self.eps_clip = cfg.eps_clip  # clip parameter for PPO
        self.entropy_coef = cfg.entropy_coef  # entropy coefficient
        self.sample_count = 0
        self.update_freq = cfg.update_freq

    @torch.no_grad()
    def sample_action(self, state):
        state = (
            torch.tensor(state, device=self.device, dtype=torch.long)
            .unsqueeze(dim=0)
            .to(self.device)
        )
        probs = self.actor(state)
        dist = Categorical(probs)
        action = dist.sample()
        return action.detach().cpu().numpy().item()
        
    def step(self, state):
        self.sample_count += 1
        state = (
            torch.tensor(state, device=self.device, dtype=torch.long)
            .unsqueeze(dim=0)
            .to(self.device)
        )
        probs = self.actor(state)
        dist = Categorical(probs)
        action = dist.sample()
        value = self.critic(state)
        return action.detach().cpu().numpy().item(), dist.log_prob(action).detach(), value.detach()

    def update(self):
        # update policy every n steps
        if self.sample_count % self.update_freq != 0:
            return
        # print("update policy")
        (
            old_states,
            old_actions,
            old_log_probs,
            old_rewards,
            old_dones,
            old_values,
        ) = self.memory.sample()
        # convert to tensor
        old_states = torch.tensor(
            np.array(old_states), device=self.device, dtype=torch.long
        )
        old_actions = torch.tensor(
            np.array(old_actions), device=self.device, dtype=torch.float32
        )
        old_log_probs = torch.tensor(
            old_log_probs, device=self.device, dtype=torch.float32
        )
        old_values = torch.tensor(
            old_values, device=self.device, dtype=torch.float32
        )
        # monte carlo estimate of state rewards
        returns = []
        for i, done in enumerate(old_dones):
            if done:
                break
        mask = [j < i for j in range(len(old_dones))]
        discounted_sum = 0
        for reward, masked in zip(reversed(old_rewards), reversed(mask)):
            if not masked:
                discounted_sum = 0
            discounted_sum = reward + (self.gamma * discounted_sum)
            returns.append(discounted_sum)
        returns.reverse()
        # Normalizing the rewards:
        returns = torch.tensor(returns, device=self.device, dtype=torch.float32)
        for _ in range(self.k_epochs):
            # compute advantage
            advantage = returns - old_values
            # get action probabilities
            probs = self.actor(old_states)
            dist = Categorical(probs)
            # get new action probabilities
            new_probs = dist.log_prob(old_actions)
            # compute ratio (pi_theta / pi_theta__old):
            ratio = torch.exp(
                new_probs - old_log_probs
            )  # old_log_probs must be detached
            # compute surrogate loss
            surr1 = ratio * advantage
            surr2 = torch.clamp(ratio, 1 - self.eps_clip, 1 + self.eps_clip) * advantage
            # compute actor loss
            actor_loss = (
                -torch.min(surr1, surr2)[mask].mean()
                + self.entropy_coef * dist.entropy().mean()
            )
            # compute critic loss
            values = self.critic(old_states)  # detach to avoid backprop through the critic
            critic_loss = F.mse_loss(returns[mask], values[mask]) 
            # take gradient step
            self.actor_optimizer.zero_grad()
            self.critic_optimizer.zero_grad()
            actor_loss.backward()
            critic_loss.backward()
            self.actor_optimizer.step()
            self.critic_optimizer.step()
        self.memory.clear()


def train(cfg: Config, env, agent: Agent, save_path):
    '''训练'''
    print("开始训练！")
    rewards = []  # 记录所有回合的奖励
    steps = []
    best_ep_reward = 0  # 记录最大回合奖励
    output_agent = None
    t_bar = tqdm(total=cfg.train_eps, ncols=120, colour="green")
    for i_ep in range(cfg.train_eps):
        ep_reward = 0  # 记录一回合内的奖励
        ep_step = 0
        state, info = env.reset()  # 重置环境，返回初始状态
        for _ in range(cfg.max_steps):
            ep_step += 1
            action, log_probs, value = agent.step(state)  # 选择动作
            next_state, reward, terminated, truncated, _ = env.step(
                action
            )  # 更新环境，返回transition
            done = terminated or truncated
            agent.memory.push((state, action, log_probs, reward, done, value))  # 保存transition
            state = next_state  # 更新下一个状态
            agent.update()  # 更新智能体
            ep_reward += reward  # 累加奖励
            if done:
                break
        if (i_ep + 1) % cfg.eval_per_episode == 0:
            sum_eval_reward = 0
            for _ in range(cfg.eval_eps):
                eval_ep_reward = 0
                state, info = env.reset()
                for _ in range(cfg.max_steps):
                    action = agent.sample_action(state)  # 选择动作
                    next_state, reward, terminated, truncated, _ = env.step(
                        action
                    )  # 更新环境，返回transition
                    done = terminated or truncated
                    state = next_state  # 更新下一个状态
                    eval_ep_reward += reward  # 累加奖励
                    if done:
                        break
                sum_eval_reward += eval_ep_reward
            mean_eval_reward = sum_eval_reward / cfg.eval_eps
            if mean_eval_reward >= best_ep_reward:
                best_ep_reward = mean_eval_reward
                output_agent = deepcopy(agent)
                tqdm.write(
                    f"回合：{i_ep+1}/{cfg.train_eps}，奖励：{ep_reward:.2f}，评估奖励：{mean_eval_reward:.2f}，最佳评估奖励：{best_ep_reward:.2f}，更新模型！"
                )
                torch.save(
                    {
                        "actor": agent.actor.state_dict(),
                        "critic": agent.critic.state_dict(),
                    },
                    save_path,
                )
            else:
                tqdm.write(
                    f"回合：{i_ep+1}/{cfg.train_eps}，奖励：{ep_reward:.2f}，评估奖励：{mean_eval_reward:.2f}，最佳评估奖励：{best_ep_reward:.2f}"
                )
        steps.append(ep_step)
        rewards.append(ep_reward)
        t_bar.set_postfix(reward=ep_reward, step=ep_step)
        t_bar.update()
    print("完成训练！")
    env.close()
    return output_agent, {'rewards': rewards}
