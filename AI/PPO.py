from collections import deque
from copy import deepcopy

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Categorical
from torch.utils.data.sampler import BatchSampler, SubsetRandomSampler
from tqdm import tqdm


class Config:
    def __init__(self) -> None:
        # self.env_name = "CartPole-v1"  # 环境名字
        self.env_name = "2048-v0"  # 环境名字
        self.mode = "train"  # train or test
        self.seed = 1  # 随机种子
        self.device = "cuda"  # device to use
        self.train_eps = 1000000  # 训练的回合数
        self.test_eps = 20  # 测试的回合数
        self.max_steps = 500  # 每个回合的最大步数
        self.eval_eps = 30  # 评估的回合数
        self.eval_per_episode = 500  # 评估的频率
        self.batch_size = 2048
        self.mini_batch_size = 256

        self.gamma = 0.99  # 折扣因子
        self.lamda = 0.98  # GAE参数
        self.k_epochs = 10  # 更新策略网络的次数
        self.actor_lr = 2e-4  # actor网络的学习率
        self.critic_lr = 2e-4  # critic网络的学习率
        self.eps_clip = 0.2  # epsilon-clip
        self.entropy_coef = 0.01  # entropy的系数
        self.update_freq = 50  # 更新频率
        self.actor_hidden_dim = 128  # actor网络的隐藏层维度
        self.actor_num_heads = 4
        self.actor_num_layers = 2
        self.critic_hidden_dim = 128  # critic网络的隐藏层维度
        self.critic_num_heads = 4
        self.critic_num_layers = 2

        self.num_actions = 4
        self.num_states = None
        self.size = None


class A2CBase(nn.Module):
    def __init__(
        self,
        input_dim,
        input_len,
        hidden_dim=256,
        num_heads=4,
        num_layers=2,
    ):
        super().__init__()
        # self.emb = nn.Embedding(input_dim + 1, hidden_dim)
        # self.pos_emb = nn.Parameter(torch.randn(input_len + 1, hidden_dim) * 0.1)
        # self.transformer = nn.TransformerEncoder(
        #     nn.TransformerEncoderLayer(
        #         d_model=hidden_dim,
        #         nhead=num_heads,
        #         dim_feedforward=hidden_dim * 4,
        #         dropout=0.0,
        #     ),
        #     num_layers=num_layers,
        # )
        self.net = nn.Sequential(
            nn.Linear(input_len, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.TransformerEncoder(
                nn.TransformerEncoderLayer(
                    d_model=hidden_dim,
                    nhead=num_heads,
                    dim_feedforward=hidden_dim * 4,
                    dropout=0.0,
                ),
                num_layers=num_layers,
            ),
            
        )

    def forward(self, x: torch.Tensor):
        # x = x + 1
        # x = torch.cat([x.new_zeros((x.shape[0], 1), dtype=torch.long), x], dim=-1)
        # x = self.emb(x) + self.pos_emb.unsqueeze(0)
        # x = self.transformer(x.permute(1, 0, 2)).permute(1, 0, 2)
        # x = x[:, 0, :]
        x = self.net(x.float())
        return x


class ActorSoftmax(A2CBase):
    def __init__(
        self,
        input_dim,
        output_dim,
        input_len,
        hidden_dim=256,
        num_heads=4,
        num_layers=2,
    ):
        super().__init__(
            input_dim,
            input_len,
            hidden_dim=hidden_dim,
            num_heads=num_heads,
            num_layers=num_layers,
        )
        self.postprocess = nn.Sequential(
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, x: torch.Tensor):
        x = super().forward(x)
        x = self.postprocess(x)
        probs = F.softmax(x, dim=-1)
        return probs


class Critic(A2CBase):
    def __init__(self, input_dim, input_len, hidden_dim=256, num_heads=4, num_layers=2):
        super().__init__(
            input_dim,
            input_len,
            hidden_dim=hidden_dim,
            num_heads=num_heads,
            num_layers=num_layers,
        )
        self.postprocess = nn.Sequential(
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, x: torch.Tensor):
        x = super().forward(x)
        x = self.postprocess(x).squeeze(-1)
        return x


class PGReplay:
    def __init__(self):
        self.buffer = deque()

    def sample(self, batch_size=None):
        '''sample all the transitions'''
        batch = list(self.buffer)
        if batch_size is not None:
            batch = batch[:batch_size]
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
            cfg.size**2,
            hidden_dim=cfg.actor_hidden_dim,
            num_heads=cfg.actor_num_heads,
            num_layers=cfg.actor_num_layers,
        ).to(self.device)
        self.critic = Critic(
            cfg.num_states,
            cfg.size**2,
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
        self.batch_size = cfg.batch_size
        self.mini_batch_size = cfg.mini_batch_size
        self.lamda = cfg.lamda

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
        return (
            action.detach().cpu().item(),
            dist.log_prob(action).detach(),
        )

    def update(self):
        if len(self.memory) < self.batch_size:
            return
        (
            old_states,
            old_actions,
            old_log_probs,
            old_rewards,
            old_next_states,
            old_dw,
            old_dones,
        ) = self.memory.sample(self.batch_size)
        self.memory.clear()
        # convert to tensor
        old_states = torch.tensor(
            np.array(old_states), device=self.device, dtype=torch.long
        )
        old_next_states = torch.tensor(
            np.array(old_next_states), device=self.device, dtype=torch.long
        )

        old_actions = torch.tensor(
            np.array(old_actions), device=self.device, dtype=torch.float32
        )
        old_log_probs = torch.tensor(
            old_log_probs, device=self.device, dtype=torch.float32
        )
        old_rewards = torch.tensor(old_rewards, device=self.device, dtype=torch.float32)
        old_dw = torch.tensor(old_dw, device=self.device, dtype=torch.float32)
        advantages = []
        # monte carlo estimate of state rewards
        with torch.no_grad():
            old_values = self.critic(old_states).detach()
            old_next_values = self.critic(old_next_states).detach()
            deltas = (
                old_rewards + self.gamma * old_next_values * (1.0 - old_dw) - old_values
            )
            gae = 0
            for delta, done in zip(
                reversed(deltas.cpu().numpy()),
                reversed(old_dones),
            ):
                gae = delta + self.gamma * self.lamda * gae * (1.0 - done)
                advantages.append(gae)
            advantages.reverse()
            advantages = torch.tensor(advantages, dtype=torch.float, device=self.device)
            values_target = advantages + old_values
            advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-5)

        t_bar = tqdm(total=self.k_epochs, ncols=120, colour="red", leave=False)
        for _ in range(self.k_epochs):
            for index in BatchSampler(
                SubsetRandomSampler(range(self.batch_size)), self.mini_batch_size, True
            ):
                dist = Categorical(self.actor(old_states[index]))
                dist_entropy = dist.entropy().mean()
                new_log_probs = dist.log_prob(old_actions[index])
                new_advantages = advantages[index]
                ratio = torch.exp(new_log_probs - old_log_probs[index])
                surr1 = ratio * new_advantages
                surr2 = (
                    torch.clamp(ratio, 1 - self.eps_clip, 1 + self.eps_clip)
                    * new_advantages
                )
                actor_loss = (
                    -torch.min(surr1, surr2).mean() - self.entropy_coef * dist_entropy
                )
                self.actor_optimizer.zero_grad()
                actor_loss.backward()
                torch.nn.utils.clip_grad_norm_(self.actor.parameters(), 0.5)
                self.actor_optimizer.step()

                new_values = self.critic(old_states[index])
                critic_loss = F.mse_loss(new_values, values_target[index])
                self.critic_optimizer.zero_grad()
                critic_loss.backward()
                torch.nn.utils.clip_grad_norm_(self.critic.parameters(), 0.5)
                self.critic_optimizer.step()
            t_bar.update()
        t_bar.close()


class RunningMeanStd:
    # Dynamically calculate mean and std
    def __init__(self, shape):  # shape:the dimension of input data
        self.n = 0
        self.mean = np.zeros(shape)
        self.S = np.zeros(shape)
        self.std = np.sqrt(self.S)

    def update(self, x):
        x = np.array(x)
        self.n += 1
        if self.n == 1:
            self.mean = x
            self.std = x
        else:
            old_mean = self.mean.copy()
            self.mean = old_mean + (x - old_mean) / self.n
            self.S = self.S + (x - old_mean) * (x - self.mean)
            self.std = np.sqrt(self.S / self.n)


class RewardScaling:
    def __init__(self, shape, gamma):
        self.shape = shape  # reward shape=1
        self.gamma = gamma  # discount factor
        self.running_ms = RunningMeanStd(shape=self.shape)
        self.R = np.zeros(self.shape)

    def __call__(self, x):
        self.R = self.gamma * self.R + x
        self.running_ms.update(self.R)
        x = x / (self.running_ms.std + 1e-8)  # Only divided std
        return x

    def reset(self):  # When an episode is done,we should reset 'self.R'
        self.R = np.zeros(self.shape)


def train(cfg: Config, env, agent: Agent, save_path):
    '''训练'''
    print("开始训练！")
    rewards = []  # 记录所有回合的奖励
    steps = []
    best_ep_reward = -999999  # 记录最大回合奖励
    output_agent = None
    t_bar = tqdm(total=cfg.train_eps, ncols=120, colour="green")
    reward_scaling = RewardScaling(shape=1, gamma=cfg.gamma)
    for i_ep in range(cfg.train_eps):
        ep_reward = 0  # 记录一回合内的奖励
        ep_step = 0
        state, info = env.reset()  # 重置环境，返回初始状态
        reward_scaling.reset()
        for i in range(cfg.max_steps):
            ep_step += 1
            action, log_probs = agent.step(state)  # 选择动作
            next_state, reward, terminated, truncated, _ = env.step(
                action
            )  # 更新环境，返回transition
            done = terminated or truncated
            dw = done and i != cfg.max_steps - 1
            reward = reward_scaling(reward).item()
            agent.memory.push(
                (state, action, log_probs, reward, next_state, dw, done)
            )  # 保存transition
            agent.update()  # 更新智能体
            state = next_state  # 更新下一个状态
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
