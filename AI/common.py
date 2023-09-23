from time import perf_counter
from copy import deepcopy

import numpy as np


class TimeCounter(object):
    def __init__(self, *args):
        self.name = None
        self.wrapper = None
        if len(args) == 0:
            return
        if len(args) == 1:
            if callable(args[0]):
                fn = args[0]

                def warpper(instance):
                    def _wrapper(*args, **kwargs):
                        start = perf_counter()
                        result = fn(instance, *args, **kwargs)
                        end = perf_counter()
                        self._print(end - start)
                        return result

                    return _wrapper

                self.wrapper = warpper
            elif isinstance(args[0], str):
                self.name = args[0]
            else:
                raise NotImplementedError

    def _print(self, interval):
        if self.name is not None:
            print(f'{self.name} cost time: {interval:.3f}s')
        else:
            print(f'Cost time: {interval:.3f}s')

    def __call__(self, fn):
        def warpper(instance):
            def _wrapper(*args, **kwargs):
                start = perf_counter()
                result = fn(instance, *args, **kwargs)
                end = perf_counter()
                self._print(end - start)
                return result

            return _wrapper

        self.wrapper = warpper
        return self

    def __get__(self, instance, owner):
        return self.wrapper(instance)

    def __enter__(self):
        self.start = perf_counter()

    def __exit__(self, *args):
        end = perf_counter()
        self._print(end - self.start)


class ParallelEnviroment:
    def __init__(self, env, num_envs=1):
        self.envs = [deepcopy(env) for _ in range(num_envs)]

    def reset(self):
        states, infos = [], []
        self.running_envs = [i for i in range(len(self.envs))]
        for env in self.envs:
            state, info = env.reset()
            states.append(state)
            infos.append(info)
        return np.array(states), infos, deepcopy(self.running_envs)

    def step(self, actions):
        states, rewards, dones, infos = [], [], [], []
        pop_ids = []
        for i, index in enumerate(self.running_envs):
            env = self.envs[index]
            state, reward, terminated, truncated, info = env.step(actions[i])
            done = terminated or truncated
            states.append(state)
            rewards.append(reward)
            dones.append(done)
            infos.append(info)
            if done:
                pop_ids.append(i)
        for i in pop_ids[::-1]:
            self.running_envs.pop(i)
        return (
            np.array(states),
            np.array(rewards),
            np.array(dones),
            infos,
            deepcopy(self.running_envs),
            pop_ids,
        )
        
    @property
    def num_states(self):
        return self.envs[0].observation_space.shape[0]

    @property
    def num_actions(self):
        return self.envs[0].action_space.n
