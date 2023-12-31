import os
import sys

import gymnasium as gym
import torch
from envs.env_2048 import Env2048

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from PPO import Agent, Config, train
from common import ParallelEnviroment


def human_run(agent: Agent):
    env = gym.make(
        cfg.env_name,
        size=size,
        render_fps=4,
        max_episode_steps=cfg.max_steps,
        max_steps=cfg.max_steps,
        max_power=max_power,
        start_power=start_power,
        power_init_range=power_init_range,
        render_mode="human",
    )
    # env = gym.make('LunarLander-v2', render_mode="human",)
    state, info = env.reset()
    rewards = 0
    for step in range(1000):
        action = agent.sample_action(state)
        state, reward, terminated, truncated, _ = env.step(
            action.item()
        )  # 更新环境，返回transition
        rewards += reward
        done = terminated or truncated
        if done:
            break


if __name__ == '__main__':
    cfg = Config()
    cfg.max_steps = 2**13 + 20
    max_power = 10
    start_power = 1
    power_init_range = 1
    size = 4
    cfg.input_dim = max_power

    env = ParallelEnviroment(
        gym.make(
            cfg.env_name,
            size=size,
            render_fps=9999,
            max_episode_steps=cfg.max_steps,
            max_steps=cfg.max_steps,
            max_power=max_power,
            start_power=start_power,
            power_init_range=power_init_range,
        ),
        2 ** 8,
    )
    # env = ParallelEnviroment(gym.make('LunarLander-v2'), 8)
    cfg.num_states = env.num_states
    cfg.num_actions = env.num_actions
    reload = True
    agent = Agent(cfg)
    save_dir = './AI/output'
    save_path = os.path.join(save_dir, 'agent.pth')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    last_epoch = 0
    if reload and os.path.exists(save_path):
        checkpoint = torch.load(save_path)
        agent.actor.load_state_dict(checkpoint['actor'])
        agent.critic.load_state_dict(checkpoint['critic'])
        last_epoch = checkpoint.get('epoch', 0)
    new_agent, info = train(cfg, env, agent, save_dir=save_dir, last_epoch=last_epoch)
    # human_run(agent)
