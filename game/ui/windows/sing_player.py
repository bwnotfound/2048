import pygame
import random
import numpy as np
from ..tools import Text, ComponentGroup, Button, Chessboard
from ..tools.common import load_image
from ..tools import Item_bag
from .window import Window
from ...core import chessboard, tool
from .page import BasePage
from .page_manager import PageManager


class Sing_player(Window, BasePage):
    def __init__(
        self,
        page_man: PageManager,
        window_width,
        window_height,
        config,
        background_color=(155, 155, 155),
    ):
        super(BasePage, self).__init__()
        self.page_man = page_man
        self.config = config
        self.window_width = window_width
        self.window_height = window_height
        self.background_img = load_image(
            config['window']['sing_player']['background_img_uri'],
            (window_width, window_height),
        )
        size = config['window']['chessboard_size']
        self.background_color = background_color
        self.chess = Chessboard(
            (window_width * 8 // 27, window_height * 19 // 32),
            (window_height * 3 // 4, window_height * 3 // 4),
            size,
            background_color=(181, 170, 156),
        )
        self.my_chessboard = chessboard.ChessBoard(
            self.config['window']['chessboard_size'],
        )
        self.my_chessboard.score = self.my_chessboard.calc_score()
        self.my_item_bag = tool.ToolsBag(12)
        self.item_possible_list = [i for i in range(1, 13)]

        self.task_str = 'task'
        self.task_text = Text(
            (window_width // 4, window_height // 8),
            self.task_str,
            font_color=(200, 140, 70),
            font=config['window']['sing_player']['task_font'],
        )
        self.score_text = Text(
            (window_width * 3 // 4, window_height * 3 // 16),
            self.score_str,
            font_color=(150, 200, 165),
        )
        self.step_text = Text(
            (window_width * 3 // 4, window_height * 5 // 16),
            self.step_str,
            font_color=(150, 200, 165),
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
        self.item_bag = Item_bag(
            (self.window_width * 9 // 24, self.window_height * 2 // 5),
            start_pos=(self.window_width * 4 // 7, self.window_height * 6 // 16),
        )

        self.show_list = ComponentGroup(
            [
                self.task_text,
                self.score_text,
                self.step_text,
                self.chess,
                self.ai_button,
                self.exit_button,
                self.item_bag,  ##这个没有show方法，自己显示
            ]
        )

    @property
    def score(self):
        return self.my_chessboard.get_total_score()

    @property
    def step(self):
        return self.my_chessboard.get_step()

    @property
    def score_str(self):
        return 'score: ' + str(self.score)

    @property
    def step_str(self):
        return 'step: ' + str(self.step)

    def show(self, window: pygame.Surface):
        self.step_text.set_text(self.step_str)
        self.score_text.set_text(self.score_str)
        self.show_list.update(
            window,
            background_img=self.background_img,
            background_color=self.background_color,
        )
        self.item_bag.show(window)

    def onclick(self):
        mouse_pos = pygame.mouse.get_pos()
        onclick_list = self.show_list.onclick(mouse_pos)
        return [part.get_text() for part in onclick_list]

    def floating_on(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.item_bag.floating_on(mouse_pos)

    def keydown(self, event: pygame.event):
        if event.key in [pygame.K_w, pygame.K_UP]:
            return 'up'
        if event.key in [pygame.K_a, pygame.K_LEFT]:
            return 'left'
        if event.key in [pygame.K_s, pygame.K_DOWN]:
            return 'down'
        if event.key in [pygame.K_d, pygame.K_RIGHT]:
            return 'right'

    def run(self, event: pygame.event.Event):
        self.floating_on()
        if event is None:
            pass
        elif event.type == pygame.MOUSEBUTTONDOWN:
            onclick_list = self.onclick()
            if 'exit' in onclick_list:
                self.page_man.del_page(self)
                return
            elif 'AI_clue' in onclick_list:
                pass  ## @bwnotfound
            elif onclick_list != []:
                if onclick_list[0] in self.item_possible_list:
                    item_num = onclick_list[0]
                    self.my_chessboard.use_tools(item_num)
                    self.my_item_bag.use_tool(item_num)
                    self.my_chessboard.score = self.my_chessboard.calc_score()
                    self.item_bag.update(self.my_item_bag.get_item_bag())
        elif event.type == pygame.KEYDOWN:
            keydown_str = self.keydown(event)
            if keydown_str in ['up', 'down', 'right', 'left']:
                if not self.chess.is_moving:
                    if keydown_str == 'up':
                        self.my_chessboard.board, _, _ = self.my_chessboard.up()
                    if keydown_str == 'down':
                        self.my_chessboard.board, _, _ = self.my_chessboard.down()
                    if keydown_str == 'right':
                        self.my_chessboard.board, _, _ = self.my_chessboard.right()
                    if keydown_str == 'left':
                        self.my_chessboard.board, _, _ = self.my_chessboard.left()
                    self.my_chessboard.add_new_num()

                    state = self.my_chessboard.game_state_check()
                    if state:
                        self.page_man.del_page(self)
                    ##TODO 还要写输赢的画面
                    ### 临时生成道具，到时候删
                    if self.my_chessboard.get_step() % 3 == 0:
                        self.my_item_bag.add_tool(random.randint(1, 12))
                        self.item_bag.update(self.my_item_bag.get_item_bag())
                    ###
                    self.chess.update(self.my_chessboard.get_board(), keydown_str)


def main(config):
    window_width = config['window']['width']
    window_height = config['window']['height']
    data = [[2, 3, 4, 8], [2, 0, 2, 16], [32, 64, 128, 256], [512, 1024, 2048, 4096]]
    window = pygame.display.set_mode((window_width, window_height))
    pygame.init()
    sing_player_page = Sing_player(
        window_width,
        window_height,
        background_img=config['window']['sing_player']['background_img_uri'],
        task_font=config['window']['sing_player']["task_font"],
    )
    # pygame.time.set_timer(pygame.USEREVENT, 5000)
    item_bag = np.array([i for i in range(1, 13)])
    sing_player_page.update(data, 100, 200, item_bag)
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
