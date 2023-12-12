import random

import numpy as np
import pygame

from ..tools import Text, ComponentGroup, Button, Chessboard, Item_bag
from ..tools.common import load_image
from .window import Window
from ...core import chessboard, tool
from .page import BasePage
from .page_manager import PageManager
from ...net import NetManager
from ..tools.common import center2rect
from .alert_window import AlertWindow


class MultiPlayer(Window, BasePage):
    def __init__(
        self,
        page_man: PageManager,
        as_server,
        net_manager: NetManager,
        config,
        keyboard_mode,
        background_color=(0, 0, 0),
    ):
        super(BasePage, self).__init__()
        self.page_man = page_man
        self.as_server = as_server
        self.net_manager = net_manager
        self.config = config
        self.keyboard_mode = keyboard_mode
        self.window_width = self.config['window']['width']
        self.window_height = self.config['window']['height']
        self.background_img = load_image(
            config['window']['multi_player']['background_img_uri'],
            (self.window_width, self.window_height),
        )
        self.background_color = background_color

        size = config['window']['chessboard_size']
        data = [[0 for _ in range(size)] for _ in range(size)]
        another_data = [[0 for _ in range(size)] for _ in range(size)]
        self.chess = Chessboard(
            (self.window_width // 5, self.window_height // 3),
            (self.window_width * 9 // 25, self.window_height * 17 // 27),
            len(data),
            background_color=(181, 170, 156),
        )
        self.another_chess = Chessboard(
            (self.window_width * 4 // 5, self.window_height * 2 // 3),
            (self.window_width * 9 // 25, self.window_height * 17 // 27),
            len(another_data),
            background_color=(181, 170, 156),
        )
        self.chessboard1 = chessboard.ChessBoard(
            self.config['window']['chessboard_size'],
        )
        self.chessboard2 = chessboard.ChessBoard(
            self.config['window']['chessboard_size'],
        )

        exit_str = 'surrender'
        self.score_text = Text(
            (self.window_width * 1 // 10, self.window_height * 19 // 27), self.score_str
        )

        self.step_text = Text(
            (self.window_width * 3 // 10, self.window_height * 19 // 27), self.step_str
        )

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

        self.chessboard1.score = self.chessboard1.calc_score()
        self.item_bag1 = tool.ToolsBag(12)
        self.item_bag2 = tool.ToolsBag(12)
        self.item_possible_list = [i for i in range(1, 13)]

        self.info_window = None

    @property
    def score(self):
        return self.chessboard1.get_total_score()

    @property
    def step(self):
        return self.chessboard1.get_step()

    @property
    def score_str(self):
        return 'score: ' + str(self.score)

    @property
    def step_str(self):
        return 'step: ' + str(self.step)

    @property
    def another_score(self):
        return self.chessboard2.get_total_score()

    @property
    def another_step(self):
        return self.chessboard2.get_step()

    @property
    def another_score_str(self):
        return 'score: ' + str(self.another_score)

    @property
    def another_step_str(self):
        return 'step: ' + str(self.another_step)

    def show(self, window: pygame.Surface):
        if self.background_img != None:
            window.blit(self.background_img, (0, 0))
        else:
            window.fill(self.background_color)
        self.score_text.set_text(self.score_str)
        self.step_text.set_text(self.step_str)
        self.another_score_text.set_text(self.another_score_str)
        self.another_step_text.set_text(self.another_step_str)
        self.item_bag.show(window)
        self.another_item_bag.show(window)
        self.show_list.update(window, background_img=self.background_img)

    def onclick(self, mouse_pos=(int, int)):
        return [part.get_text() for part in self.show_list.onclick(mouse_pos)]

    def keydown(self, event: pygame.event):
        if event.key == pygame.K_w:
            return '1-up'
        if event.key == pygame.K_a:
            return '1-left'
        if event.key == pygame.K_s:
            return '1-down'
        if event.key == pygame.K_d:
            return '1-right'
        if self.keyboard_mode:
            if event.key == pygame.K_UP:
                return '2-up'
            if event.key == pygame.K_LEFT:
                return '2-left'
            if event.key == pygame.K_DOWN:
                return '2-down'
            if event.key == pygame.K_RIGHT:
                return '2-right'

    def click_exit(self):
        self.show_list.del_compo(self.info_window)
        self.info_window = None
        self.exit()

    def exit(self):
        self.page_man.del_page(self)
        if self.net_manager is not None:
            self.net_manager.disconnect()

    def floating_on(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.item_bag.floating_on(mouse_pos)

    def run(self, event: pygame.event.Event):
        self.floating_on()
        need_synthesis = False
        if event is None:
            pass
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            onclick_list = self.onclick(mouse_pos)
            if 'surrender' in onclick_list:
                self.exit()
                return
            elif onclick_list != []:
                if onclick_list[0] in self.item_possible_list:
                    need_synthesis = True
                    item_num = onclick_list[0]
                    item_num1 = self.item_bag.onclick(mouse_pos)
                    if item_num == item_num1:
                        self.chessboard1.use_tools(item_num)
                        self.item_bag1.use_tool(item_num)
                        self.chessboard1.score = self.chessboard1.calc_score()
                        self.item_bag.update(self.item_bag1.get_item_bag())
                        self.chess.board = (
                            self.chess.pre_board
                        ) = self.chessboard1.get_board()
                    elif self.keyboard_mode:
                        self.chessboard2.use_tools(item_num)
                        self.item_bag2.use_tool(item_num)
                        self.chessboard2.score = self.chessboard2.calc_score()
                        self.another_item_bag.update(self.item_bag2.get_item_bag())
                        self.another_chess.board = (
                            self.another_chess.pre_board
                        ) = self.chessboard2.get_board()
        elif event.type == pygame.KEYDOWN:
            if self.info_window is not None:
                return
            key = self.keydown(event)
            if not self.chess.is_moving:
                if key in [
                    '1-up',
                    '1-down',
                    '1-right',
                    '1-left',
                    '2-up',
                    '2-down',
                    '2-right',
                    '2-left',
                ]:
                    (
                        target_chessboard,
                        target_item_bag,
                        target_tool_bag,
                        target_chess,
                    ) = (
                        (self.chessboard1, self.item_bag, self.item_bag1, self.chess)
                        if key[0] == '1'
                        else (
                            self.chessboard2,
                            self.another_item_bag,
                            self.item_bag2,
                            self.another_chess,
                        )
                    )
                    who = 1 if key[0] == '1' else 2
                    key = key[2:]

                    state = target_chessboard.game_state_check()
                    if state == 1:
                        self.info_window = AlertWindow(
                            "You Win!" if who == 1 else "You Lose!",
                            center2rect(
                                (self.window_width // 2, self.window_height // 2),
                                (self.window_width // 2, self.window_height // 2),
                            ),
                            self.click_exit,
                        )
                        self.show_list.add_compo(self.info_window)
                        return
                    elif state == 2:
                        self.info_window = AlertWindow(
                            "You Lose!" if who == 1 else "You Win!",
                            center2rect(
                                (self.window_width // 2, self.window_height // 2),
                                (self.window_width // 2, self.window_height // 2),
                            ),
                            self.click_exit,
                        )
                        self.show_list.add_compo(self.info_window)
                        return

                    need_synthesis = True
                    if key == 'up':
                        target_chessboard.board, _, _ = target_chessboard.up()
                    if key == 'down':
                        target_chessboard.board, _, _ = target_chessboard.down()
                    if key == 'right':
                        target_chessboard.board, _, _ = target_chessboard.right()
                    if key == 'left':
                        target_chessboard.board, _, _ = target_chessboard.left()

                    target_chessboard.add_new_num()

                    ### 临时生成道具，到时候删
                    if target_chessboard.get_step() % 3 == 0:
                        target_tool_bag.add_tool(random.randint(1, 12))
                        target_item_bag.update(target_tool_bag.get_item_bag())
                    ###
                    target_chess.update(target_chessboard.get_board(), key)
        if not self.keyboard_mode:
            if need_synthesis:
                self.net_manager.send(self.chessboard1.pack_data())
            data = self.net_manager.recv(recv_all=True)
            if len(data) > 0:
                data = data[-1]
            else:
                data = None
            if data is not None:
                self.chessboard2.load_data(data)
                self.another_chess.board = self.another_chess.pre_board = self.chessboard2.get_board()
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
    multi_player_page = MultiPlayer(
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
