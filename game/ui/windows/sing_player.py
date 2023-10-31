import pygame
import numpy as np
from ..tools import Text, ComponentGroup, Button, Chessboard
from ..tools.common import load_image
from ..tools import item_bag
from .window import Window

class Sing_player(Window):
    def __init__(
        self,
        window_width,
        window_height,
        config,
        background_color=(155,155,155)
    ):
        self.window_width = window_width
        self.window_height = window_height
        self.background_img = load_image(config['window']['sing_player']['background_img_uri'], (window_width, window_height))
        self.background_color = background_color
        self.score = 0
        self.step = 0
        self.task_str='task'
        self.task_text=Text(
            (window_width//4,window_height//8),
            self.task_str,
            font_color=(200,140,70),
            font=config['window']['sing_player']['task_font'],
        )
        self.score_text = Text(
            (window_width * 3 // 4, window_height *3// 16),
            self.score_str,
            font_color=(150,200,165),
        )
        self.step_text = Text(
            (window_width * 3 // 4, window_height * 5 // 16), self.step_str,font_color=(150,200,165),
        )
        size=config['window']['sing_player']['chessboard_size']
        self.data = [[0 for _ in range(size)] for _ in range(size)]
        self.chess = Chessboard(
            (window_width *8// 27, window_height * 19 // 32),
            (window_height * 3 // 4, window_height * 3 // 4),
            size,
            background_color=(181, 170, 156),
        )
        self.ai_button = Button(
            (window_width * 14 // 16, window_height * 14 // 16),
            'AI_clue',
            size=(200, 50),
        )
        self.exit_button = Button(
            (window_width * 14 // 16, window_height * 15 // 16),
            'exit',
            size=(200, 50),
            background_color=(255, 255, 255, 100),
        )
        self.item_bag_num = np.zeros(12,int)
        self.item_bag=item_bag((self.window_width*9//24,self.window_height*2//5),start_pos=(self.window_width*4//7,self.window_height*6//16))

        self.show_list = ComponentGroup(
            [
                self.task_text,
                self.score_text,
                self.step_text,
                self.chess,
                self.ai_button,
                self.exit_button,
                self.item_bag  ##这个没有show方法，自己显示
            ]
        )

    @property
    def score_str(self):
        return 'score: ' + str(self.score)

    @property
    def step_str(self):
        return 'step: ' + str(self.step)

    def show(self, window:pygame.Surface):
        self.chess.update(self.data)
        self.step_text.set_text(self.step_str)
        self.score_text.set_text(self.score_str)
        self.show_list.update(
            window,
            background_img=self.background_img,
            background_color=self.background_color,
        )
        window.blit(self.item_bag.get_surface(),(self.window_width*4//7,self.window_height*6//16))

    def onclick(self):
        mouse_pos = pygame.mouse.get_pos()
        onclick_list = self.show_list.onclick(mouse_pos)
        return [part.get_text() for part in onclick_list]

    def update(self, data, score, step, item_bag:np.ndarray, item_pos=[]):
        self.data = data
        self.score = score
        self.step = step
        self.item_bag_num=item_bag
        self.item_bag.update(self.item_bag_num)
              
        

    def keydown(self, event: pygame.event):
        if event.key in [pygame.K_w, pygame.K_UP]:
            return 'up'
        if event.key in [pygame.K_a, pygame.K_LEFT]:
            return 'left'
        if event.key in [pygame.K_s, pygame.K_DOWN]:
            return 'down'
        if event.key in [pygame.K_d, pygame.K_RIGHT]:
            return 'right'


def main(config):
    window_width = config['window']['width']
    window_height = config['window']['height']
    data = [[2, 3, 4, 8], [2, 0, 2, 16], [32, 64, 128, 256], [512, 1024, 2048, 4096]]
    window = pygame.display.set_mode((window_width, window_height))
    pygame.init()
    sing_player_page = Sing_player(window_width, window_height, background_img=config['window']['sing_player']['background_img_uri'],task_font=config['window']['sing_player']["task_font"])
    # pygame.time.set_timer(pygame.USEREVENT, 5000)
    item_bag=np.array([i for i in range(1,13)])
    sing_player_page.update(data, 100, 200,item_bag)
    sing_player_page.show(window)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                onclick_list = sing_player_page.onclick()
            elif event.type == pygame.KEYDOWN:
                keydown_str = sing_player_page.keydown(event)
                print(keydown_str)

        sing_player_page.show(window)
        pygame.display.flip()
