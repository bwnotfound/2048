from .text import Text
import pygame
import os

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
    65536: (246, 124, 95)
}


class Chessboard():
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
            self.text_dict[k] = surf
            
        self.board = [[0 for _ in range(row_num)] for _ in range(row_num)]

    def _show_part(self, center, value, width, height, window: pygame.Surface):
        window.blit(
            self.text_dict[value], (center[0] - width // 2, center[1] - height // 2)
        )

    def show(self, window: pygame.Surface):
        for i in range(self.row_num):
            for j in range(self.row_num):
                if self.board[i][j] in color_dict.keys():
                    self._show_part(
                        (
                            self.size[0] * (2 * j + 1) // self.row_num // 2,
                            self.size[1] * (2 * i + 1) // self.row_num // 2,
                        ),
                        self.board[i][j],
                        self.size[0] * 0.8 // self.row_num,
                        self.size[1] * 0.8 // self.row_num,
                        self.chessboard_surface,
                    )
        window.blit(
            self.chessboard_surface,
            self.rect,
        )

    # data:记录棋盘数据的二维数组
    def update(self, data):
        self.board = data
