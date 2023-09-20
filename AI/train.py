import os
import sys

import gymnasium as gym
import torch
from envs.env_2048 import Env2048

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from PPO import Agent, Config, train


def human_run(agent: Agent):
    env = gym.make(
        cfg.env_name,
        size=4,
        render_fps=5,
        max_episode_steps=1000,
        max_power=10,
        start_power=1,
        power_init_range=0,
        render_mode="human",
    )
    state, info = env.reset()
    rewards = 0
    for step in range(1000):
        action = agent.sample_action(state)
        state, reward, terminated, truncated, _ = env.step(action)  # 更新环境，返回transition
        rewards += reward
        done = terminated or truncated
        if done:
            break


if __name__ == '__main__':
    cfg = Config()
    cfg.max_steps = 200
    cfg.update_freq = cfg.max_steps
    max_power=10
    start_power=1
    size = 4
    env = gym.make(
        cfg.env_name,
        size=size,
        render_fps=9999,
        max_episode_steps=cfg.max_steps,
        max_power=max_power,
        start_power=start_power,
        power_init_range=0,
    )
    cfg.size = size
    cfg.num_states = max_power
    cfg.num_actions = env.action_space.n
    reload = False
    agent = Agent(cfg)
    save_dir = './AI/output'
    save_path = os.path.join(save_dir, 'agent.pth')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    if reload and os.path.exists(save_path):
        checkpoint = torch.load(save_path)
        agent.actor.load_state_dict(checkpoint['actor'])
        agent.critic.load_state_dict(checkpoint['critic'])
    new_agent, info = train(cfg, env, agent, save_path=save_path)
    # human_run(agent)
