import os
import sys

import gymnasium as gym
import torch
from env_2048 import Env2048


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
        state, reward, terminated, truncated, _ = env.step(
            action
        )  # 更新环境，返回transition
        rewards += reward
        done = terminated or truncated
        if done:
            break
  
    
if __name__ == '__main__':
    cfg = Config()
    cfg.max_steps = 200
    cfg.update_freq = cfg.max_steps
    env = gym.make(
        cfg.env_name,
        size=4,
        render_fps=9999,
        max_episode_steps=cfg.max_steps,
        max_power=10,
        start_power=1,
        power_init_range=0,
    )
    cfg.num_states = env.observation_space.shape[0]
    cfg.num_actions = env.action_space.n
    reload = True
    agent = Agent(cfg)
    if reload and os.path.exists('./AI/output/agent.pth'):
        checkpoint = torch.load('./AI/output/agent.pth')
        agent.actor.load_state_dict(checkpoint['actor'])
        agent.critic.load_state_dict(checkpoint['critic'])
    # new_agent, info = train(cfg, env, agent, save_path='./AI/output/agent.pth')
    human_run(agent)
    
