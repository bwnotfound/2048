import os

import pygame

from .common import fill_rect, get_font


##方形按钮
class Button(pygame.sprite.Sprite):
    ## center:tuple[int,int] 按钮中心
    # text:str 按钮文字
    # title_size:int 文字大小
    # size:int 按钮检测大小     为None则自动检测为文字的范围
    ## font:str 字体    None为默认字体，系统字体直接输入字体名，导入字体输入文件路径

    def __init__(
        self,
        center,
        text,
        size=None,
        font_size=60,
        font_color=(255, 255, 255),
        background_color=None,
        border_width=2,
        border_color=None,
        border_radius=0,
        font=None,
        antialias=True,
    ):
        self.center = center
        self.text = text
        self.font_size = font_size
        self.border_width = border_width
        self.border_radius = border_radius
        self.antialias = antialias
        self.font = get_font(font, font_size)
        self.font_color = pygame.Color(*font_color)
        if background_color is None:
            self.background_color = pygame.Color((0, 0, 0, 0))
        else:
            self.background_color = pygame.Color(*background_color)
        if border_color is None:
            self.border_color = (0, 0, 0, 0)
        else:
            self.border_color = pygame.Color(*border_color)
        if size is None:
            size = self.font.render(self.text, antialias, self.font_color).get_size()
        self.size = size
        self.onclick_font_color = tuple(min(i + 20, 255) for i in self.font_color)
        self.is_onclick = False

        self.rect = pygame.Rect(
            *[center[i] - self.size[i] / 2 for i in range(2)], *self.size
        )
        self._draw()

    def _draw(self):
        self.image = pygame.Surface(self.size).convert_alpha()
        fill_rect(
            self.image,
            pygame.Rect(0, 0, *self.size),
            self.background_color,
            self.border_radius,
        )
        pygame.draw.rect(
            self.image,
            self.border_color,
            pygame.Rect(0, 0, self.rect.width, self.rect.height),
            self.border_width,
            self.border_radius,
        )
        self.font_image = self.font.render(
            self.text,
            self.antialias,
            self.font_color if not self.is_onclick else self.onclick_font_color,
        )
        font_rect = self.font_image.get_rect()
        self.image.blit(
            self.font_image,
            (
                (self.size[0] - font_rect.width) // 2,
                (self.size[1] - font_rect.height) // 2,
            ),
        )
        self.image.convert()

    def show(self, window: pygame.Surface):
        window.blit(self.image, self.rect)

    def onclick(self, mouse_pos):
        if (
            mouse_pos[0] > self.center[0] - self.size[0] // 2
            and mouse_pos[0] < self.center[0] + self.size[0] // 2
            and mouse_pos[1] > self.center[1] - self.size[1] // 2
            and mouse_pos[1] < self.center[1] + self.size[1] // 2
        ):
            if self.is_onclick == False:
                self.is_onclick = True
                self._draw()
            return True
        else:
            if self.is_onclick == True:
                self.is_onclick = False
                self._draw()
            return False

    def set_text(self, text: str):
        self.text = text
        self._draw()

    def get_text(self):
        return self.text
