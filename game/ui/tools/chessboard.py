from .text import Text
import pygame
import os
import numpy as np
from time import perf_counter

color_dict = {
    3: (200, 55, 65),
    0: (220, 220, 220),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
    4096: (238, 228, 218),
    8192: (237, 194, 46),
    16384: (242, 177, 121),
    32768: (245, 149, 99),
    65536: (246, 124, 95),
}


class Chessboard:
    def __init__(
        self, center, size, row_num=4, background_color=(0, 0, 0, 0), img=None
    ):
        self.chessboard_surface = pygame.Surface(size)
        self.chessboard_surface = self.chessboard_surface.convert_alpha()
        self.center = center
        self.size = size
        self.row_num = row_num
        self.background_color = background_color
        self.img = img
        self.rect = pygame.Rect(
            self.center[0] - self.size[0] // 2,
            self.center[1] - self.size[1] // 2,
            self.size[0],
            self.size[1],
        )
        if self.img != None:
            if not os.path.exists(self.img):
                print(f'img {self.img} not exists')
            else:
                image = pygame.image.load(self.img)
                scaled_img = pygame.transform.scale(
                    image, (self.rect.width, self.rect.height)
                )
                self.chessboard_surface.blit(scaled_img, self.rect.topleft)
        else:
            pygame.draw.rect(
                self.chessboard_surface, self.background_color, (0, 0, *self.size)
            )
        self.text_dict = {}
        for k in color_dict.keys():
            w, h = (
                self.size[0] * 0.8 // self.row_num,
                self.size[1] * 0.8 // self.row_num,
            )
            surf = pygame.Surface((w, h))
            color = color_dict[k]
            pygame.draw.rect(surf, color, (0, 0, w, h))
            show_text = Text(
                (w // 2, h // 2),
                str(k),
                font_size=int((w + h) // 6),
                background_color=color,
                font_color=(0, 0, 0),
            )
            if k != 0:
                show_text.show(surf)
            # self.text_dict[k] = surf
            self.text_dict[k] = (
                surf,
                color,
                show_text,
                (0, 0, w, h),
                show_text.get_font_alpha(),
            )

        self.board = [[0 for _ in range(row_num)] for _ in range(row_num)]
        self.pre_board = [[0 for _ in range(row_num)] for _ in range(row_num)]

        self.is_moving = False
        self.moving_sec = 0.2
        self.last_sec = 0
        self.move_direction = None

    def time_rate(self, after_ratio=0.0):
        last_sec = self.last_sec + self.moving_sec * after_ratio
        rate = (perf_counter() - last_sec) / self.moving_sec
        rate = max(min(rate, 1), 0)
        return rate

    def calc_position(self, start_pos, end_pos):
        rate = self.time_rate()
        if rate > 0.5:
            pass
        return (
            (end_pos[0] - start_pos[0]) * rate + start_pos[0],
            (end_pos[1] - start_pos[1]) * rate + start_pos[1],
        )

    def get_position(self, i, j):
        return (
            self.size[0] * (2 * j + 1) // self.row_num // 2,
            self.size[1] * (2 * i + 1) // self.row_num // 2,
        )

    def get_size(self):
        return (
            self.size[0] * 0.8 // self.row_num,
            self.size[1] * 0.8 // self.row_num,
        )

    def _show_part(
        self, center, value, width, height, window: pygame.Surface, alpha=1.0
    ):
        (surf, color, text, rect, pre_alpha) = self.text_dict[value]
        if pre_alpha != alpha and value != 0:
            text.set_font_alpha(alpha * 255)
            pygame.draw.rect(surf, color, rect)
            text.show(surf)
            self.text_dict[value] = (surf, color, text, rect, alpha)
        window.blit(surf, (center[0] - width // 2, center[1] - height // 2))

    def _show(self, window: pygame.Surface):
        for i in range(self.row_num):
            for j in range(self.row_num):
                if self.board[i][j] in color_dict.keys():
                    self._show_part(
                        self.get_position(i, j),
                        self.board[i][j],
                        *self.get_size(),
                        self.chessboard_surface,
                    )
        window.blit(
            self.chessboard_surface,
            self.rect,
        )

    def show(self, window: pygame.Surface):
        if not self.is_moving:
            self._show(window)
            has_changed = False
            for i in range(self.row_num):
                for j in range(self.row_num):
                    if self.pre_board[i][j] != self.board[i][j]:
                        has_changed = True
                        break
                if has_changed:
                    break
            if not has_changed:
                return

            self.is_moving = True
            self.last_sec = perf_counter()
            self.moved_xy_dict = {}
            pre_board_np = np.array(self.pre_board, dtype=int).copy()
            # 不同方向统一到左移计算
            if self.move_direction == 'up':
                pre_board_np = np.rot90(pre_board_np, 1)
            elif self.move_direction == 'down':
                pre_board_np = np.rot90(pre_board_np, 3)
            elif self.move_direction == 'right':
                pre_board_np = np.rot90(pre_board_np, 2)

            for i in range(self.row_num):
                count = 0
                for j in range(self.row_num):
                    if pre_board_np[i][j] != 0:
                        pre_board_np[i][count] = pre_board_np[i][j]
                        if count != j:
                            pre_board_np[i][j] = 0
                            self.moved_xy_dict[(i, j)] = ((i, count), (i, j))
                        count += 1

            for i in range(self.row_num):
                for j in range(1, self.row_num):
                    if (
                        pre_board_np[i][j - 1] == pre_board_np[i][j]
                        and pre_board_np[i][j] != 0
                    ):
                        pre_board_np[i][j - 1] *= 2
                        pre_board_np[i][j] = 0
                        for data in self.moved_xy_dict.values():
                            if data[0] == (i, j):
                                self.moved_xy_dict[data[1]] = ((i, j - 1), data[1])
                                break
                        else:
                            self.moved_xy_dict[(i, j)] = ((i, j - 1), (i, j))
            new_dict = {}
            for k in self.moved_xy_dict.keys():
                self.moved_xy_dict[k] = self.moved_xy_dict[k][0]
                i, j = k
                p = self.moved_xy_dict[k][1]
                if self.move_direction == 'up':
                    new_dict[(j, self.row_num - 1 - i)] = (
                        p,
                        self.row_num - 1 - i,
                    )
                elif self.move_direction == 'down':
                    new_dict[(self.row_num - 1 - j, i)] = (
                        self.row_num - 1 - p,
                        i,
                    )
                elif self.move_direction == 'right':
                    new_dict[(self.row_num - 1 - i, self.row_num - 1 - j)] = (
                        self.row_num - 1 - i,
                        self.row_num - 1 - p,
                    )
                else:
                    new_dict[k] = (i, p)
            self.moved_xy_dict = new_dict
        pygame.draw.rect(
            self.chessboard_surface, self.background_color, (0, 0, *self.size)
        )
        moving_block = []
        for i in range(self.row_num):
            for j in range(self.row_num):
                if self.pre_board[i][j] in color_dict.keys():
                    self._show_part(
                        self.get_position(i, j),
                        0,
                        *self.get_size(),
                        self.chessboard_surface,
                    )
                    if (i, j) in self.moved_xy_dict.keys():
                        moving_block.append((i, j))
                    elif (i, j) in self.moved_xy_dict.values():
                        if self.time_rate() > 0.75:
                            self._show_part(
                                self.get_position(i, j),
                                self.board[i][j],
                                *self.get_size(),
                                self.chessboard_surface,
                                # alpha=self.time_rate(0.7),
                            )
                    else:
                        self._show_part(
                            self.get_position(i, j),
                            self.board[i][j],
                            *self.get_size(),
                            self.chessboard_surface,
                        )
        for ax in moving_block:
            i, j = ax
            self._show_part(
                self.calc_position(
                    self.get_position(i, j),
                    self.get_position(*self.moved_xy_dict[(i, j)]),
                ),
                self.pre_board[i][j],
                *self.get_size(),
                self.chessboard_surface,
                alpha=1 - self.time_rate(0.8),
            )
        window.blit(
            self.chessboard_surface,
            self.rect,
        )

        if self.time_rate() == 1:
            self.is_moving = False
            self.pre_board = np.array(self.board, dtype=int)

    # data:记录棋盘数据的二维数组
    def update(self, data, direction):
        self.board = data
        self.move_direction = direction
