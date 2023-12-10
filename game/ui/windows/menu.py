import random
import os

import pygame

# from ...main import GameManager
from ..tools import Button, Text, ComponentGroup
from .page import BasePage
from ...main import GameManager
from .online_player import OnlineChoice
from .page_manager import PageManager


class Menu(BasePage):
    def __init__(
        self,
        page_man: PageManager,
        config,
        rect: pygame.Rect,
        background_img=None,
        background_color=None,
        menu_font=None,
    ):
        super().__init__()
        self.page_man = page_man
        self.config = config
        r = random.randrange(75, 150)
        g = random.randrange(125, 200)
        b = random.randrange(100, 175)
        self.rect = rect
        window_width = rect.width
        window_height = rect.height
        self.menu_title = Text(
            (window_width // 2, window_height // 8),
            '2048',
            font_color=(r, g, b),
            font_size=window_width // 10,
            font=menu_font,
        )
        self.start_btn = Button(
            (window_width // 2, window_height * 5 // 16),
            'sing_player',
            font_color=(
                r + random.randint(10, 50),
                g + random.randint(20, 50),
                b + random.randint(20, 50),
            ),
            font_size=100,
            font=menu_font,
        )
        self.multiplayer_btn = Button(
            (window_width // 2, window_height * 8 // 16),
            'multiplayer',
            font_color=(
                r + random.randint(10, 50),
                g + random.randint(20, 50),
                b + random.randint(20, 50),
            ),
            font_size=100,
            font=menu_font,
        )
        self.classic_btn = Button(
            (window_width // 2, window_height * 11 // 16),
            'classic',
            font_color=(
                r + random.randint(10, 50),
                g + random.randint(20, 50),
                b + random.randint(20, 50),
            ),
            font_size=100,
            font=menu_font,
        )
        self.setting_btn = Button(
            (window_width // 2, window_height * 14 // 16),
            'setting',
            font_color=(
                r + random.randint(10, 50),
                g + random.randint(20, 50),
                b + random.randint(20, 50),
            ),
            font_size=100,
            font=menu_font,
        )
        self.show_list = ComponentGroup(
            [
                self.menu_title,
                self.start_btn,
                self.multiplayer_btn,
                self.setting_btn,
                self.classic_btn,
            ]
        )
        if background_img is not None:
            if not os.path.exists(background_img):
                print(f'img {background_img} not exists')
            else:
                image = pygame.image.load(background_img)
                self.background_img = pygame.transform.scale(
                    image, (window_width, window_height)
                ).convert()
        else:
            self.background_img = None
        self.background_color = background_color

    def run(self, event: pygame.event.Event):
        from .sing_player import Sing_player
        from .setting import Setting

        if event is None:
            pass
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            onclick_list = self.onclick(mouse_pos)
            if 'sing_player' in onclick_list:
                self.page_man.add_page(
                    Sing_player(
                        self.page_man,
                        window_height=self.config['window']['height'],
                        window_width=self.config['window']['width'],
                        config=self.config,
                    )
                )
                self.page_man.del_page(self)
            elif 'multiplayer' in onclick_list:
                self.page_man.add_page(OnlineChoice(self.page_man, self.config))
                self.page_man.del_page(self)
            elif 'setting' in onclick_list:
                self.page_man.add_page(Setting(self.page_man, self.config))
                self.page_man.del_page(self)

    def close(self):
        self.page_man.del_page(self)

    def show(self, window: pygame.Surface):
        if self.visible and len(self.pages) == 0:
            self.show_list.update(
                window, self.background_img, self.background_color, rect=self.rect
            )
        for page in self.pages:
            page.show(window)

    ## 返回被点击的所有组件对应的字符串的列表
    def onclick(self, mouse_pos):
        if len(self.pages) != 0:
            return []
        return [
            part.get_text() for part in self.show_list.onclick(mouse_pos)
        ]  # TODO: 没有检查是否有get_text方法。建议做成基类


def main(config):
    window_width = config['window']['width']
    window_height = config['window']['height']

    window = pygame.display.set_mode((window_width, window_height))
    pygame.init()
    # pygame.time.set_timer(pygame.USEREVENT, 5000)
    menu_page = Menu(
        background_img=config['window']['menu']['background_img_uri'],
        menu_font=config['window']['menu']['menu_font_uri'],
    )
    menu_page.show(window)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                onclick_list = menu_page.onclick(mouse_pos)
                if 'sing_player' in onclick_list:
                    print('sing_player')
                    pass  # 运行单人游戏界面
                elif 'multiplayer' in onclick_list:
                    print('multi')
                    pass  # 运行多人游戏界面
                elif 'setting' in onclick_list:
                    print('setting')
                    pass  # 运行设置界面
            menu_page.show(window)
        pygame.display.flip()
