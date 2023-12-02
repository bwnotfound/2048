import random

import numpy as np
import pygame

from ..tools import Text, ComponentGroup, Button, Chessboard, Item_bag
from ..tools.common import load_image
from .window import Window
from ...main import GameManager
from ...common import TimeCounter
from ...core import chessboard, tool
from .page import BasePage


class Multi_player(Window, BasePage):
    def __init__(
        self,
        parent: BasePage,
        config,
        background_color=(0, 0, 0),
    ):
        super(BasePage, self).__init__()
        self.parent = parent
        self.config = config
        self.window_width = self.config['window']['width']
        self.window_height = self.config['window']['height']
        self.background_img = load_image(
            config['window']['multi_player']['background_img_uri'],
            (self.window_width, self.window_height),
        )
        self.score = 0
        self.step = 0
        self.background_color = background_color

        size = config['window']['chessboard_size']
        self.data = [[0 for _ in range(size)] for _ in range(size)]

        self.another_score = 0
        self.another_step = 0
        self.another_data = [[0 for _ in range(size)] for _ in range(size)]

        exit_str = 'surrender'
        score_str = 'score: ' + str(self.score)
        self.score_text = Text(
            (self.window_width * 1 // 10, self.window_height * 19 // 27), score_str
        )

        step_str = 'step: ' + str(self.step)
        self.step_text = Text(
            (self.window_width * 3 // 10, self.window_height * 19 // 27), step_str
        )
        self.chess = Chessboard(
            (self.window_width // 5, self.window_height // 3),
            (self.window_width * 9 // 25, self.window_height * 17 // 27),
            len(self.data),
            background_color=(181, 170, 156),
        )

        self.item_bag_num = np.zeros(12, int)
        self.item_bag = Item_bag(
            (self.window_width // 3, self.window_height * 5 // 27),
            start_pos=(self.window_width * 2 // 54, self.window_height * 20 // 27),
        )
        self.exit_button = Button(
            (self.window_width * 1 // 5, self.window_height * 26 // 27), exit_str
        )

        another_score_str = 'score: ' + str(self.another_score)
        self.another_score_text = Text(
            (self.window_width * 7 // 10, self.window_height * 1 // 27),
            another_score_str,
        )
        another_step_str = 'step: ' + str(self.another_step)
        self.another_step_text = Text(
            (self.window_width * 9 // 10, self.window_height * 1 // 27),
            another_step_str,
        )
        # chess=Chessboard((self.window_width//2,self.window_height//2),(self.window_width,self.window_height))
        self.another_chess = Chessboard(
            (self.window_width * 4 // 5, self.window_height * 2 // 3),
            (self.window_width * 9 // 25, self.window_height * 17 // 27),
            len(self.another_data),
            background_color=(181, 170, 156),
        )
        self.another_item_bag_num = np.zeros(12, int)
        self.another_item_bag = Item_bag(
            (self.window_width // 3, self.window_height * 5 // 27),
            start_pos=(self.window_width * 34 // 54, self.window_height * 2 // 27),
        )
        self.another_exit_button = Button(
            (self.window_width * 4 // 5, self.window_height * 8 // 27),
            exit_str,
        )
        self.show_list = ComponentGroup(
            [
                self.score_text,
                self.step_text,
                self.chess,
                self.exit_button,
                self.another_score_text,
                self.another_step_text,
                self.another_chess,
                self.another_exit_button,
                self.item_bag,
                self.another_item_bag,
            ]
        )

        self.chessboard1 = chessboard.ChessBoard(
            self.config['window']['chessboard_size'],
        )
        self.chessboard2 = chessboard.ChessBoard(
            self.config['window']['chessboard_size'],
        )
        self.chessboard1.score = self.chessboard1.calc_score()
        self.item_bag1 = tool.ToolsBag(12)
        self.item_bag2 = tool.ToolsBag(12)
        self.item_possible_list = [i for i in range(1, 13)]

    def show(self, window: pygame.Surface):
        if self.background_img != None:
            window.blit(self.background_img, (0, 0))
        else:
            window.fill(self.background_color)

        ##道具还没写
        self.show_list.update(window, background_img=self.background_img)
        window.blit(self.item_bag.get_surface(), self.item_bag.start_pos)
        window.blit(
            self.another_item_bag.get_surface(), self.another_item_bag.start_pos
        )

    def onclick(self, mouse_pos=(int, int)):
        return [part.get_text() for part in self.show_list.onclick(mouse_pos)]

    def update(
        self,
        data,
        score,
        step,
        another_data,
        another_score,
        another_step,
        item_bag_num: np.ndarray,
        another_item_bag_num: np.ndarray,
    ):
        self.data = data
        self.score = score
        self.step = step
        self.another_data = another_data
        self.another_score = another_score
        self.another_step = another_step
        self.chess.update(data)
        self.score_text.set_text(f'score: {self.score}')
        self.step_text.set_text(f'step: {self.step}')
        self.another_chess.update(another_data)
        self.another_score_text.set_text(f'score: {self.another_score}')
        self.another_step_text.set_text(f'step: {self.another_step}')
        self.item_bag_num = item_bag_num
        self.another_item_bag_num = another_item_bag_num
        self.item_bag.update(self.item_bag_num)
        self.another_item_bag.update(self.another_item_bag_num)

    def keydown(self, event: pygame.event):
        ret = []
        if event.key == pygame.K_w:
            ret.append('1-up')
        if event.key == pygame.K_UP:
            ret.append('2-up')
        if event.key == pygame.K_a:
            ret.append('1-left')
        if event.key == pygame.K_LEFT:
            ret.append('2-left')
        if event.key == pygame.K_s:
            ret.append('1-down')
        if event.key == pygame.K_DOWN:
            ret.append('2-down')
        if event.key == pygame.K_d:
            ret.append('1-right')
        if event.key == pygame.K_RIGHT:
            ret.append('2-right')
        return ret

    def run(self, event: pygame.event.Event):
        if event is None:
            pass
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            onclick_list = self.onclick(mouse_pos)
            if 'surrender' in onclick_list:
                self.close()
            elif onclick_list != []:
                if onclick_list[0] in self.item_possible_list:
                    item_num = onclick_list[0]
                    item_num1 = self.item_bag.onclick(mouse_pos)
                    if item_num == item_num1:
                        self.chessboard1.use_tools(item_num)
                        self.item_bag1.use_tool(item_num)
                        self.chessboard1.score = self.chessboard1.calc_score()
                    else:
                        self.chessboard2.use_tools(item_num)
                        self.item_bag2.use_tool(item_num)
                        self.chessboard2.score = self.chessboard2.calc_score()
        elif event.type == pygame.KEYDOWN:
            with TimeCounter("keydown"):
                keydown_str = self.keydown(event)
                for key in keydown_str:
                    if key in ['1-up', '1-down', '1-right', '1-left']:
                        if key == '1-up':
                            self.chessboard1.board, _, _ = self.chessboard1.up()
                        if key == '1-down':
                            (
                                self.chessboard1.board,
                                _,
                                _,
                            ) = self.chessboard1.down()
                        if key == '1-right':
                            (
                                self.chessboard1.board,
                                _,
                                _,
                            ) = self.chessboard1.right()
                        if key == '1-left':
                            (
                                self.chessboard1.board,
                                _,
                                _,
                            ) = self.chessboard1.left()
                        self.chessboard1.add_new_num()
                        state = self.chessboard1.game_state_check()
                        if state:
                            self.close()
                        ##TODO 还要写输赢的画面
                        ### 临时生成道具，到时候删
                        if self.chessboard1.get_step() % 3 == 0:
                            self.item_bag1.add_tool(random.randint(1, 12))
                        ###

                    if key in ['2-up', '2-down', '2-right', '2-left']:
                        if key == '2-up':
                            self.chessboard2.board, _, _ = self.chessboard2.up()
                        if key == '2-down':
                            (
                                self.chessboard2.board,
                                _,
                                _,
                            ) = self.chessboard2.down()
                        if key == '2-right':
                            (
                                self.chessboard2.board,
                                _,
                                _,
                            ) = self.chessboard2.right()
                        if key == '2-left':
                            (
                                self.chessboard2.board,
                                _,
                                _,
                            ) = self.chessboard2.left()
                        self.chessboard2.add_new_num()
                        state = self.chessboard2.game_state_check()
                        if state:
                            self.close()
                        ##TODO 还要写输赢的画面
                        ### 临时生成道具，到时候删
                        if self.chessboard2.get_step() % 3 == 0:
                            self.item_bag2.add_tool(random.randint(1, 12))
                        ###
        self.update(
            data=self.chessboard1.get_board(),
            score=self.chessboard1.get_total_score(),
            step=self.chessboard1.get_step(),
            another_data=self.chessboard2.get_board(),
            another_score=self.chessboard2.get_total_score(),
            another_step=self.chessboard2.get_step(),
            item_bag_num=self.item_bag1.get_item_bag(),
            another_item_bag_num=self.item_bag2.get_item_bag(),
        )
        ##


def main(config):
    data = [[2, 3, 4, 8], [2, 0, 2, 16], [32, 64, 128, 256], [512, 1024, 2048, 4096]]
    another_data = [
        [2, 3, 4, 8],
        [2, 0, 2, 16],
        [512, 1024, 2048, 4096],
        [32, 64, 128, 256],
    ]
    window = pygame.display.set_mode(
        (config['window']['width'], config['window']['height'])
    )
    pygame.init()
    multi_player_page = Multi_player(
        background_img=config['window']['multi_player']['background_img_uri']
    )
    # pygame.time.set_timer(pygame.USEREVENT, 5000)
    multi_player_page.update(data, 100, 200, another_data, 150, 250)
    multi_player_page.show(window)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                multi_player_page.onclick()
            elif event.type == pygame.KEYDOWN:
                keydown_str = multi_player_page.keydown(event)
                print(keydown_str)
        multi_player_page.show(window)
        pygame.display.flip()
