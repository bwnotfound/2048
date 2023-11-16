import pygame

from .common import abstract_onclick_comp,abstract_show_comp

# 拉链 在一个范围内通过鼠标点击线的相对位置来决定数字大小
class Slider(abstract_onclick_comp,abstract_show_comp):
    def __init__(
        self, center, size=60, mouse_percent=0.5, data_range=(0, 100), font=None
    ):
        self.center = center
        self.size = size
        self.length = size * 5
        self.mouse_percent = mouse_percent
        self.data_range = data_range
        self.font = font

    def show(self, window: pygame.Surface):
        font = pygame.font.Font(self.font, self.size)
        num = int(self.mouse_percent * (self.data_range[1] - self.data_range[0]))
        title = font.render(str(num), True, (150, 150, 150))
        title_rect = title.get_rect()
        title_rect.center = (self.center[0], self.center[1] - self.size // 3)
        window.blit(title, title_rect)
        pygame.draw.line(
            window,
            (103, 157, 180),
            (self.center[0] - self.length // 2, self.center[1]),
            (self.center[0] + self.length // 2, self.center[1]),
            width=5,
        )
        pygame.draw.line(
            window,
            (169, 220, 219),
            (
                self.center[0] - self.length // 2 + self.mouse_percent * self.length,
                self.center[1] - 1,
            ),
            (
                self.center[0]
                - self.length // 2
                + self.mouse_percent * self.length
                + 8,
                self.center[1] - 1,
            ),
            width=10,
        )

    def onclick(self, mouse_pos):
        if (
            mouse_pos[0] > self.center[0] - self.length // 2
            and mouse_pos[0] < self.center[0] + self.length // 2
            and mouse_pos[1] > self.center[1] - 10
            and mouse_pos[1] < self.center[1] + 10
        ):
            self.mouse_percent = (
                mouse_pos[0] - self.center[0] + self.length // 2
            ) / self.length
            return True
        else:
            return False

    def get_text(self):
        return int(self.mouse_percent * (self.data_range[1] - self.data_range[0]))
