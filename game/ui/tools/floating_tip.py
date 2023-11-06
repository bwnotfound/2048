import pygame
import time

from .common import get_font


class Floating_tip:
    def __init__(
        self,
        floating_rect:pygame.Rect,
        center,
        text,
        floating_time=2,
        font_color=(255, 255, 255),
        font_size=60,
        font=None,
        antialias=True,
        background_color=(0, 0, 0, 0),
    ):
        self.center = center
        self.text = text
        self.floating_rect=floating_rect
        self.floating_time=floating_time
        self.font_color = font_color
        self.font_size = font_size
        self.font = get_font(font, font_size)
        self.antialias = antialias
        self.has_floating_time=0
        self.last_floating_time=time.time()<<2
        self.size = self.font.render(self.text, antialias, self.font_color).get_size()
        self.rect = pygame.Rect(
            *[center[i] - self.size[i] // 2 for i in range(2)], *self.size
        )
        self.background_color = background_color
        self.is_showing=False
        self._draw()

    def _draw(self):
        self.image = pygame.Surface(self.size).convert_alpha()
        if self.is_showing:
            self.image.fill(self.background_color)
            self.font_image = self.font.render(self.text, self.antialias, self.font_color)
            self.image.blit(
                self.font_image,
                (0, 0),
            )
        else:
            self.image.fill((0,0,0,0))

    def show(self, window: pygame.Surface):
        window.blit(self.image, self.rect)

    def get_text(self):
        return self.text

    def set_text(self, text: str):
        self.text = text
        self.size = self.font.render(
            self.text, self.antialias, self.font_color
        ).get_size()
        self.rect = pygame.Rect(
            *[self.center[i] - self.size[i] // 2 for i in range(2)], *self.size
        )
        self._draw()

    def floating_on(self,mouse_pos):
        now_time=time.time()
        if self.is_showing:
            if not self.floating_rect.collidepoint(mouse_pos[0],mouse_pos[1]):
                self.is_showing=False
                self.last_floating_time=now_time<<2
                self.has_floating_time=0
                self._draw()
            else:
                self.has_floating_time+=now_time-self.last_floating_time
                self.last_floating_time=now_time 
            return
        else:
            if self.floating_rect.collidepoint(mouse_pos[0],mouse_pos[1]):
                self.has_floating_time+=now_time-self.last_floating_time
                if self.has_floating_time>self.floating_time:
                    self.is_showing=True   
                    self._draw()
                self.last_floating_time=now_time
                
                