import pygame
from ..tools import Text, ComponentGroup, Button
from .page_manager import PageManager


class AlertWindow:
    def __init__(
        self,
        msg,
        rect: pygame.Rect,  # (w, h)
        click_fn,
        btn_msg='OK',
        background_color=(155, 155, 155),
    ):
        self.rect = rect
        self.btn_msg = btn_msg
        self.click_fn = click_fn
        self.background_color = background_color
        self.text = Text(
            (rect.w // 2, rect.h // 2),
            msg,
            font_color=(200, 140, 70),
            font_size=40,
        )
        self.btn = Button(
            (rect.w // 2, rect.h * 3 // 4),
            btn_msg,
            font_color=(200, 140, 70),
            font_size=60,
        )
        self.surf = pygame.Surface((rect.w, rect.h))
        self.show_list = ComponentGroup([self.text, self.btn])
        self.show_list.update(
            self.surf,
            background_color=self.background_color,
        )

    def onclick(self, mouse_pos):
        mouse_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
        onclick_list = self.show_list.onclick(mouse_pos)
        result = [part.get_text() for part in onclick_list]
        if self.btn_msg in result:
            self.click_fn()
        return False

    def show(self, window: pygame.Surface):
        window.blit(self.surf, self.rect)
