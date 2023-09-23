import random
import time

import pygame
from pygame.sprite import RenderPlain

from ..tools import Button
from ..tools import Text
from ..tools import Slider
from ..tools import InputBox
from ..tools import Need_to_show
from ..tools import Chessboard


def menu(window: pygame.Surface):
    window_width = 1280
    window_height = 720

    r = random.randrange(100, 255)
    g = random.randrange(100, 255)
    b = random.randrange(100, 255)
    menu_title = Text(
        (window_width // 2, window_height // 8),
        '2048',
        font_color=(r, g, b),
        font_size=window_width // 10,
        font='game\\ui\\src\\font\\Milky Mania.ttf',
    )
    start = Button(
        (window_width // 2, window_height * 5 // 16),
        'start',
        size=(500, 120),
        border_radius=10,
        font_size=100,
        font='arial',
    )
    multiplayer = Button(
        (window_width // 2, window_height * 8 // 16),
        'multiplayer',
        size=(500, 121),
        border_radius=10,
        font_size=100,
        font='arial',
    )
    setting = Button(
        (window_width // 2, window_height * 11 // 16),
        'Settings',
        size=(500, 120),
        border_radius=10,
        font_size=100,
        font='arial',
    )

    zip_temp = Slider((window_width // 2, window_height * 14 // 16))
    input_blank = InputBox((window_width // 2, window_height * 15 // 16))

    show_list = Need_to_show(
        [menu_title, start, multiplayer, setting, zip_temp, input_blank]
    )
    show_list.show(window)
    
    ## 测试代码
    chess=Chessboard((200,200),(400,400))
    data=[
        [2,3,4,8],
        [2,0,2,16],
        [32,64,128,256],
        [512,1024,2048,4096]
    ]
    chess.update(data)

    last_time = time.time()

    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start.onclick(mouse_pos):
                    print('start')
                    pass  # 运行单人游戏界面
                elif multiplayer.onclick(mouse_pos):
                    print('multi')
                    pass  # 运行多人游戏界面
                elif setting.onclick(mouse_pos):
                    print('setting')
                    pass  # 运行设置界面
                elif zip_temp.onclick(mouse_pos):
                    show_list.update(window)
                elif input_blank.onclick(mouse_pos):
                    show_list.update(window)
            elif event.type == pygame.KEYDOWN:
                if time.time() - last_time > 0.15:
                    last_time = time.time()
                    ## 当时是限制输入的是ip地址（只有数字和'.'）随缘修改
                    if event.key == pygame.K_BACKSPACE:
                        if input_blank.is_ready() == True:
                            input_blank.del_text()
                    elif pygame.K_0 <= event.key <= pygame.K_9:
                        if input_blank.is_ready() == True:
                            input_blank.add_text(str(event.key - pygame.K_0))
                    elif pygame.K_PERIOD == event.key:
                        if input_blank.is_ready() == True:
                            input_blank.add_text('.')
                    show_list.update(window)
            pygame.display.flip()


def main():
    window_width = 1280
    window_height = 720

    window = pygame.display.set_mode((window_width, window_height))
    pygame.init()
    # pygame.time.set_timer(pygame.USEREVENT, 5000)
    while True:
        menu(window)
        window.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
