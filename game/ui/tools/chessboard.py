from .text import Text
import pygame
import os

color_dict = {
    3: (200, 55, 65),
    0: (220, 220, 220),
    2: (217, 219, 215),
    4: (214, 218, 210),
    8: (211, 217, 205),
    16: (208, 216, 200),
    32: (205, 215, 195),
    64: (202, 214, 190),
    128: (199, 213, 185),
    256: (196, 212, 180),
    512: (193, 211, 175),
    1024: (190, 210, 170),
    2048: (187, 209, 165),
    4096: (184, 208, 160),
    8192: (181, 207, 155),
    16384: (178, 206, 150),
}


class Chessboard:
    def __init__(self, center, size, row_num=4, background_color=(0, 0, 0), img=None):
        self.center = center
        self.size = size
        self.row_num = row_num
        self.background_color = background_color
        self.data = [[0 for _ in range(row_num)] for _ in range(row_num)]
        self.img = img

    def _show_part(self, center, value, width, height, window):
        rect = pygame.Rect(
            center[0] - width // 2, center[1] - height // 2, width, height
        )
        color = color_dict[value]
        show_text = Text(
            center,
            str(value),
            font_size=int((width + height) // 6),
            background_color=color_dict[value],
            font_color=(0, 0, 0),
        )
        pygame.draw.rect(window, color, rect)
        if value != 0:
            show_text.show(window)

    def show(self, window):
        rect = pygame.Rect(
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
                scaled_img = pygame.transform.scale(image, (rect.width, rect.height))
                window.blit(scaled_img, rect.topleft)
        else:
            pygame.draw.rect(window, self.background_color, rect)
        for i in range(self.row_num):
            for j in range(self.row_num):
                if self.data[i][j] in color_dict.keys():
                    self._show_part(
                        (
                            self.center[0]
                            - self.size[0] // 2
                            + self.size[0] * (2 * j + 1) // self.row_num // 2,
                            self.center[1]
                            - self.size[1] // 2
                            + self.size[1] * (2 * i + 1) // self.row_num // 2,
                        ),
                        self.data[i][j],
                        self.size[0] * 0.8 // self.row_num,
                        self.size[1] * 0.8 // self.row_num,
                        window,
                    )

    # data:记录棋盘数据的二维数组
    def update(self, data):
        self.data = data
