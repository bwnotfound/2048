import random
import time
import os

import pygame
from pygame.sprite import RenderPlain

from ..tools import Button, Text, Slider, InputBox, Comp_Collection, Chessboard


class Menu:
    def __init__(
        self,
        window_width=1280,
        window_height=720,
        background_img=None,
        background_color=(0, 0, 0),
    ):
        r = random.randrange(75, 150)
        g = random.randrange(125, 200)
        b = random.randrange(100, 175)
        self.menu_title = Text(
            (window_width // 2, window_height // 8),
            '2048',
            font_color=(r, g, b),
            font_size=window_width // 10,
            font='game\\ui\\src\\font\\Milky Mania.ttf',
        )
        self.start = Button(
            (window_width // 2, window_height * 5 // 16),
            'start',
            font_color=(
                r + random.randint(10, 50),
                g + random.randint(20, 50),
                b + random.randint(20, 50),
            ),
            font_size=100,
            font='game\\ui\\src\\font\\Milky Mania.ttf',
        )
        self.multiplayer = Button(
            (window_width // 2, window_height * 8 // 16),
            'multiplayer',
            font_color=(
                r + random.randint(10, 50),
                g + random.randint(20, 50),
                b + random.randint(20, 50),
            ),
            font_size=100,
            font='game\\ui\\src\\font\\Milky Mania.ttf',
        )
        self.setting = Button(
            (window_width // 2, window_height * 11 // 16),
            'setting',
            font_color=(
                r + random.randint(10, 50),
                g + random.randint(20, 50),
                b + random.randint(20, 50),
            ),
            font_size=100,
            font='game\\ui\\src\\font\\Milky Mania.ttf',
        )
        self.show_list = Comp_Collection(
            [self.menu_title, self.start, self.multiplayer, self.setting]
        )
        if background_img != None:
            if not os.path.exists(background_img):
                print(f'img {background_img} not exists')
            else:
                image = pygame.image.load(background_img)
                self.background_img = pygame.transform.scale(
                    image, (window_width, window_height)
                )
        else:
            self.background_img = None
        self.background_color = background_color

    def show(self, window: pygame.Surface):
        self.show_list.update(window, self.background_img)

    ## 返回被点击的所有组件对应的字符串的列表
    def onclick(self):
        mouse_pos = pygame.mouse.get_pos()
        return [part.get_text() for part in self.show_list.onclick(mouse_pos)]

    

def main():
    window_width = 1280
    window_height = 720

    window = pygame.display.set_mode((window_width, window_height))
    pygame.init()
    # pygame.time.set_timer(pygame.USEREVENT, 5000)
    menu_page = Menu(background_img='game\\ui\\src\\img\\menu_bg.jpg')
    menu_page.show(window)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                onclick_list = menu_page.onclick()
                if 'start' in onclick_list:
                    print('start')
                    pass  # 运行单人游戏界面
                elif 'multiplayer' in onclick_list:
                    print('multi')
                    pass  # 运行多人游戏界面
                elif 'setting' in onclick_list:
                    print('setting')
                    pass  # 运行设置界面
            menu_page.show(window)
