import gymnasium as gym
from gymnasium import spaces
import pygame
import numpy as np


class Env2048(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"]}

    def __init__(
        self,
        render_mode=None,
        size=6,
        render_fps=10,
        max_episode_steps=200,
        max_power=10,
        start_power=1,
        power_init_range=0,
    ):
        self.window_size = 512  # The size of the PyGame window
        self.size = size
        self.max_power = max_power
        self.render_fps = render_fps
        assert start_power >= 1 and start_power + power_init_range <= max_power
        self.start_power = start_power
        self.power_init_range = power_init_range
        self.max_episode_steps = max_episode_steps

        self.observation_space = spaces.Box(0, max_power, shape=(size**2,), dtype=int)

        # We have 4 actions, corresponding to "right", "up", "left", "down"
        self.action_space = spaces.Discrete(4)

        # "right", "up", "left", "down"
        self._action_to_direction = {
            0: np.array([1, 0]),
            1: np.array([0, -1]),
            2: np.array([-1, 0]),
            3: np.array([0, 1]),
        }

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        """
        If human-rendering is used, `self.window` will be a reference
        to the window that we draw to. `self.clock` will be a clock that is used
        to ensure that the environment is rendered at the correct framerate in
        human-mode. They will remain `None` until human-mode is used for the
        first time.
        """
        self.window = None
        self.clock = None

    def _get_obs(self):
        return self._board.copy().reshape(-1)

    def _get_info(self):
        return {}

    def _res_empty_element_list(self):
        result = []
        for i in range(self.size):
            for j in range(self.size):
                if self._board[i, j] == 0:
                    result.append((i, j))
        return result

    def _random_add_element(self):
        res_list = self._res_empty_element_list()
        if len(res_list) == 0:
            return False
        init_num_pos = res_list[
            self.np_random.integers(0, len(res_list), size=1, dtype=int)[0]
        ]
        self._board[init_num_pos[0], init_num_pos[1]] = self.np_random.integers(
            self.start_power,
            self.start_power + self.power_init_range,
            size=1,
            dtype=int,
            endpoint=True,
        )[0]
        return True

    def reset(self, seed=None, options=None):
        # We need the following line to seed self.np_random
        super().reset(seed=seed)

        # Choose the agent's location uniformly at random
        self._board = np.full((self.size, self.size), 0, dtype=np.int32)
        self.step_count = 0
        assert self._random_add_element()

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    def _merge_block_list(self, block_list):
        if len(block_list) == 0:
            return block_list, []
        result = []
        reward_list = []
        i = 0
        while i < len(block_list):
            if i == len(block_list) - 1:
                result.append(block_list[i])
                break
            if block_list[i] == block_list[i + 1]:
                result.append(block_list[i] + 1)
                reward_list.append(block_list[i] + 1)
                i += 2
            else:
                result.append(block_list[i])
                i += 1
        if len(reward_list) > 0:
            result, returned_reward_list = self._merge_block_list(result)
            reward_list = reward_list + returned_reward_list
        return result, reward_list

    def step(self, action):
        # Map the action (element of {0,1,2,3}) to the direction we walk in
        direction = self._action_to_direction[action]
        reward = -1
        self.step_count += 1
        if direction[0] != 0:
            d = direction[0]
            for i in range(self.size):
                custom_iter = (
                    range(self.size - 1, -1, -1) if d == 1 else range(self.size)
                )
                # 编写2048的核心算法
                block_list = []
                for j in custom_iter:
                    if self._board[i, j] == 0:
                        continue
                    block_list.append(self._board[i, j])
                    self._board[i, j] = 0
                if len(block_list) == 0:
                    continue
                block_list, reward_list = self._merge_block_list(block_list)
                for r in reward_list:
                    reward += r
                for j in range(len(block_list)):
                    pos = j if d == -1 else self.size - 1 - j
                    self._board[i, pos] = block_list[j]
        else:
            d = direction[1]
            for i in range(self.size):
                custom_iter = (
                    range(self.size - 1, -1, -1) if d == 1 else range(self.size)
                )
                # 编写2048的核心算法
                block_list = []
                for j in custom_iter:
                    if self._board[j, i] == 0:
                        continue
                    block_list.append(self._board[j, i])
                    self._board[j, i] = 0
                if len(block_list) == 0:
                    continue
                block_list, reward_list = self._merge_block_list(block_list)
                for r in reward_list:
                    reward += r
                for j in range(len(block_list)):
                    pos = j if d == -1 else self.size - 1 - j
                    self._board[pos, i] = block_list[j]

        # An episode is done iff the agent has reached the target
        terminated = (
            not self._random_add_element() or self._board.max() == self.max_power
        )
        truncated = self.step_count >= self.max_episode_steps
        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, terminated, truncated, info

    def render(self):
        if self.render_mode == "rgb_array":
            return self._render_frame()

    def _render_frame(self):
        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode((self.window_size, self.window_size))
        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        canvas = pygame.Surface((self.window_size, self.window_size))
        canvas.fill((255, 255, 255))
        pix_square_size = (
            self.window_size / self.size
        )  # The size of a single grid square in pixels

        # add some gridlines
        for x in range(self.size + 1):
            pygame.draw.line(
                canvas,
                0,
                (0, pix_square_size * x),
                (self.window_size, pix_square_size * x),
                width=3,
            )
            pygame.draw.line(
                canvas,
                0,
                (pix_square_size * x, 0),
                (pix_square_size * x, self.window_size),
                width=3,
            )

        for i in range(self.size):
            for j in range(self.size):
                ratio = (self._board[i, j]) / (self.max_power + 20)
                r, g, b = 255 * (1 - ratio), 255 * (1 - ratio), 255 * (1 - ratio)
                pygame.draw.rect(
                    canvas,
                    (r, g, b),
                    (
                        pix_square_size * j + 3,
                        pix_square_size * i + 3,
                        pix_square_size - 6,
                        pix_square_size - 6,
                    ),
                )

        # 显示数字
        for i in range(self.size):
            for j in range(self.size):
                if self._board[i, j] == 0:
                    continue
                text = pygame.font.SysFont("arial", 30).render(
                    str(2 ** self._board[i, j]), True, (0, 0, 0)
                )
                canvas.blit(
                    text,
                    (
                        pix_square_size * j
                        + pix_square_size / 2
                        - text.get_width() / 2,
                        pix_square_size * i
                        + pix_square_size / 2
                        - text.get_height() / 2,
                    ),
                )

        if self.render_mode == "human":
            # The following line copies our drawings from `canvas` to the visible window
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()

            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to keep the framerate stable.
            self.clock.tick(self.render_fps)
        else:  # rgb_array
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2)
            )

    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
