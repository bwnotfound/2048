import pygame

from .common import get_font


class Text:
    def __init__(
        self,
        center,
        text,
        font_color=(255, 255, 255),
        font_size=60,
        font=None,
        antialias=True,
        background_color=(0, 0, 0, 0),
    ):
        self.center = center
        self.text = text
        self.font_color = font_color
        self.font_size = font_size
        self.font = get_font(font, font_size)
        self.antialias = antialias
        self.background_color = background_color
        self.changed = False
        self._draw()

    def _draw(self):
        self.size = self.font.render(
            self.text, self.antialias, self.font_color
        ).get_size()
        self.rect = pygame.Rect(
            *[self.center[i] - self.size[i] // 2 for i in range(2)], *self.size
        )
        self.image = pygame.Surface(self.size).convert_alpha()
        self.image.fill(self.background_color)
        self.font_image = self.font.render(self.text, self.antialias, self.font_color)
        self.image.blit(
            self.font_image,
            (0, 0),
        )

    def show(self, window: pygame.Surface):
        if self.changed:
            self._draw()
            self.changed = False
        window.blit(self.image, self.rect)

    def get_text(self):
        return self.text

    def set_text(self, text: str):
        if text == self.text:
            return
        self.changed = True
        self.text = text
