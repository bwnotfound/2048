from collections import deque
from copy import deepcopy
import os

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Categorical
from torch.utils.data.sampler import BatchSampler, SubsetRandomSampler
from torch.utils.tensorboard.writer import SummaryWriter
from tqdm import tqdm


class Config:
    def __init__(self) -> None:
        # self.env_name = "CartPole-v1"  # 环境名字
        self.env_name = "2048-v0"  # 环境名字
        self.mode = "train"  # train or test
        self.seed = 1  # 随机种子
        self.device = "cuda"  # device to use
        self.train_eps = 1000000  # 训练的回合数
        self.max_steps = 1000  # 每个回合的最大步数
        self.eval_eps = 512  # 评估的回合数
        self.eval_per_episode = 2000  # 评估的频率
        self.batch_size = 32768
        self.mini_batch_size = 512

        self.gamma = 0.99  # 折扣因子
        self.lamda = 0.98  # GAE参数
        self.k_epochs = 10  # 更新策略网络的次数
        self.actor_lr = 1e-5  # actor网络的学习率
        self.critic_lr = 1e-5  # critic网络的学习率
        self.eps_clip = 0.2  # epsilon-clip
        self.entropy_coef = 0.01  # entropy的系数
        self.actor_hidden_dim = 128  # actor网络的隐藏层维度
        self.actor_num_heads = 4
        self.actor_num_layers = 3
        self.critic_hidden_dim = 128  # critic网络的隐藏层维度
        self.critic_num_heads = 4
        self.critic_num_layers = 3

        self.num_actions = None
        self.num_states = None
        self.input_dim = None


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
        self.net = nn.Sequential(
            nn.Linear(input_len, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
        )

    def forward(self, x: torch.Tensor):
        return self.net(x)


# class A2CBase(nn.Module):
#     def __init__(
#         self,
#         input_dim,
#         input_len,
#         hidden_dim=256,
#         num_heads=4,
#         num_layers=2,
#     ):
#         super().__init__()
#         self.emb = nn.Embedding(input_dim + 1, hidden_dim)
#         self.pos_emb = nn.Parameter(torch.zeros(1, input_len + 1, hidden_dim))
#         self.encoder = nn.TransformerEncoder(
#             nn.TransformerEncoderLayer(
#                 d_model=hidden_dim,
#                 nhead=num_heads,
#                 dim_feedforward=hidden_dim * 4,
#                 dropout=0.0,
#             ),
#             num_layers=num_layers,
#         )
#         self.next_net = nn.Sequential(
#             nn.Linear(hidden_dim, hidden_dim),
#             nn.Tanh(),
#         )

#     def forward(self, x: torch.Tensor):
#         x = torch.cat(
#             [
#                 torch.zeros(x.shape[0], 1, dtype=torch.long, device=x.device),
#                 x,
#             ],
#             dim=1,
#         )
#         x = self.emb(x) + self.pos_emb
#         x = self.encoder(x.permute(1, 0, 2)).permute(1, 0, 2)
#         x = x[:, 0, :]
#         x = self.next_net(x)
#         return x


class ActorSoftmax(A2CBase):
    def __init__(
        self,
        input_dim,
        input_len,
        output_dim,
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
            cfg.input_dim,
            cfg.num_states,
            cfg.num_actions,
            hidden_dim=cfg.actor_hidden_dim,
            num_heads=cfg.actor_num_heads,
            num_layers=cfg.actor_num_layers,
        ).to(self.device)
        self.critic = Critic(
            cfg.input_dim,
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
        self.batch_size = cfg.batch_size
        self.mini_batch_size = cfg.mini_batch_size
        self.lamda = cfg.lamda

    @torch.no_grad()
    def sample_action(self, state):
        state = torch.tensor(state, device=self.device, dtype=torch.float32).to(
            self.device
        )
        if len(state.shape) == 1:
            state.unsqueeze_(0)
        probs = self.actor(state)
        dist = Categorical(probs)
        action = dist.sample()
        return action.detach().cpu().numpy()

    @torch.no_grad()
    def step(self, state):
        state = torch.tensor(state, device=self.device, dtype=torch.float32).to(
            self.device
        )
        if len(state.shape) == 1:
            state.unsqueeze_(0)
        probs = self.actor(state)
        dist = Categorical(probs)
        action = dist.sample()
        return (
            action.detach().cpu().numpy(),
            dist.log_prob(action).detach().cpu().numpy(),
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
            np.array(old_states), device=self.device, dtype=torch.float32
        )
        old_next_states = torch.tensor(
            np.array(old_next_states), device=self.device, dtype=torch.float32
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


def train(cfg: Config, parallel_env, agent: Agent, save_dir):
    '''训练'''
    print("开始训练！")
    writer = SummaryWriter(save_dir)
    best_ep_reward = -999999  # 记录最大回合奖励
    output_agent = None
    t_bar = tqdm(total=cfg.train_eps, ncols=120, colour="green")
    reward_scalings = [
        RewardScaling(shape=1, gamma=cfg.gamma) for _ in range(len(parallel_env.envs))
    ]
    for i_ep in range(cfg.train_eps):
        ep_reward = [0 for _ in range(len(parallel_env.envs))]  # 记录一回合内的奖励
        ep_step = [0 for _ in range(len(parallel_env.envs))]
        states, infos, indices = parallel_env.reset()  # 重置环境，返回初始状态
        for reward_scaling in reward_scalings:
            reward_scaling.reset()
        (
            store_states,
            store_actions,
            store_log_probs,
            store_rewards,
            store_next_states,
            store_dws,
            store_dones,
        ) = (
            [[] for _ in range(states.shape[0])],
            [[] for _ in range(states.shape[0])],
            [[] for _ in range(states.shape[0])],
            [[] for _ in range(states.shape[0])],
            [[] for _ in range(states.shape[0])],
            [[] for _ in range(states.shape[0])],
            [[] for _ in range(states.shape[0])],
        )
        for i in range(cfg.max_steps):
            actions, log_probs = agent.step(states)  # 选择动作
            next_states, rewards, dones, _, next_indices, pop_ids = parallel_env.step(
                actions
            )  # 更新环境，返回transition
            for k, j in enumerate(indices):
                store_states[j].append(states[k])
                store_actions[j].append(actions[k])
                store_log_probs[j].append(log_probs[k])
                reward = rewards[k]
                ep_reward[j] += reward  # 累加奖励
                reward = reward_scalings[j](reward).item()
                store_rewards[j].append(reward)
                store_next_states[j].append(next_states[k])
                store_dws[j].append(dones[k] and i != cfg.max_steps - 1)
                store_dones[j].append(dones[k])
                ep_step[j] += 1
            states = next_states  # 更新下一个状态
            leave_ids = [j for j in range(len(indices)) if j not in pop_ids]
            states = states[leave_ids]
            if states.shape[0] == 0:
                break
            indices = next_indices
        for i in range(len(parallel_env.envs)):
            for j in range(len(store_states[i])):
                agent.memory.push(
                    (
                        store_states[i][j],
                        store_actions[i][j],
                        store_log_probs[i][j],
                        store_rewards[i][j],
                        store_next_states[i][j],
                        store_dws[i][j],
                        store_dones[i][j],
                    )
                )
        agent.update()  # 更新智能体
        if (i_ep + 1) % (cfg.eval_per_episode // len(parallel_env.envs)) == 0:
            sum_eval_reward = 0
            eval_reward_step = 0
            for _ in range(0, cfg.eval_eps, len(parallel_env.envs)):
                states, infos, indices = parallel_env.reset()
                for _ in range(cfg.max_steps):
                    actions = agent.sample_action(states)  # 选择动作
                    (
                        next_states,
                        rewards,
                        dones,
                        _,
                        next_indices,
                        pop_ids,
                    ) = parallel_env.step(
                        actions
                    )  # 更新环境，返回transition
                    for k, j in enumerate(indices):
                        sum_eval_reward += rewards[k]  # 累加奖励
                    states = next_states  # 更新下一个状态
                    leave_ids = [j for j in range(len(indices)) if j not in pop_ids]
                    states = states[leave_ids]
                    if states.shape[0] == 0:
                        break
                    indices = next_indices
                eval_reward_step += 1
            mean_eval_reward = sum_eval_reward / (
                eval_reward_step * len(parallel_env.envs)
            )
            if mean_eval_reward >= best_ep_reward:
                best_ep_reward = mean_eval_reward
                output_agent = deepcopy(agent)
                tqdm.write(
                    f"回合：{(i_ep+1) * len(parallel_env.envs)}/{cfg.train_eps}，评估奖励：{mean_eval_reward:.2f}，最佳评估奖励：{best_ep_reward:.2f}，更新模型！"
                )
                torch.save(
                    {
                        "actor": agent.actor.state_dict(),
                        "critic": agent.critic.state_dict(),
                    },
                    os.path.join(save_dir, "agent.pth"),
                )
            else:
                tqdm.write(
                    f"回合：{(i_ep+1) * len(parallel_env.envs)}/{cfg.train_eps}，评估奖励：{mean_eval_reward:.2f}，最佳评估奖励：{best_ep_reward:.2f}"
                )
        ep_reward = np.mean(ep_reward).item()
        ep_step = np.mean(ep_step).item()
        writer.add_scalar("Train/ep_reward", ep_reward, (i_ep + 1) * len(parallel_env.envs))
        writer.add_scalar("Train/ep_step", ep_step, (i_ep + 1) * len(parallel_env.envs))
        t_bar.set_postfix(reward=ep_reward, step=ep_step)
        t_bar.update(len(parallel_env.envs))
    print("完成训练！")
    # env.close()
    return output_agent
