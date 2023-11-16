import toml
import random

import pygame
import numpy as np

from .ui import windows
from .core import *
from .common import TimeCounter
from .net import NetManager

class Game:
    def __init__(self,config_path:str):
        self.now_page = 'menu'
        self.config_path=config_path
        config = toml.load(config_path)
        self.config = config

    def start(self):
        statu_set = ('menu', 'sing_player', 'multi_player', 'setting')
        self.window_width = self.config['window']['width']
        self.window_height = self.config['window']['height']
        window = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.init()
        while True:
            if self.now_page == 'menu':
                ret = self._menu_start(window)
            elif self.now_page == 'sing_player':
                ret = self._sing_player_start(window)
            elif self.now_page == 'multi_player':
                ret = self._multi_player_page(window)
            elif self.now_page =='setting':
                ret = self._setting_page(window)

            if ret in statu_set:
                self.now_page = ret

    def _menu_start(self, window: pygame.Surface):
        menu_page = windows.Menu(
            window_width=window.get_width(),
            window_height=window.get_height(),
            background_img=self.config['window']['menu']['background_img_uri'],
            menu_font=self.config['window']['menu']['menu_font_uri'],
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
                        return 'sing_player'  # 运行单人游戏界面
                    elif 'multiplayer' in onclick_list:
                        return 'multi_player'  # 运行多人游戏界面
                    elif 'setting' in onclick_list:
                        return 'setting'  # 运行设置界面
                menu_page.show(window)
            pygame.display.flip()

    def _sing_player_start(self, window: pygame.Surface):
        sing_player_page = windows.Sing_player(
            window_height=window.get_height(),
            window_width=window.get_width(),
            config=self.config,
        )
        my_chessboard = chessboard.ChessBoard(
            self.config['window']['chessboard_size'],
        )
        my_chessboard.score = my_chessboard.calc_score()
        my_item_bag = tool.ToolsBag(12)
        item_possible_list = [i for i in range(1, 13)]
        sing_player_page.update(
            data=my_chessboard.get_board(),
            score=my_chessboard.get_total_score(),
            step=my_chessboard.get_step(),
            item_bag=my_item_bag.get_item_bag(),
        )
        sing_player_page.show(window)
        pygame.display.flip()
        while True:
            if sing_player_page.floating_on():
                sing_player_page.update(
                    data=my_chessboard.get_board(),
                    score=my_chessboard.score * 100000 + my_chessboard.prizescore,
                    step=my_chessboard.get_step(),
                    item_bag=my_item_bag.get_item_bag(),
                )
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    onclick_list = sing_player_page.onclick()
                    if 'exit' in onclick_list:
                        return 'menu'
                    elif 'AI_clue' in onclick_list:
                        pass  ## @bwnotfound
                    elif onclick_list != []:
                        if onclick_list[0] in item_possible_list:
                            item_num = onclick_list[0]
                            my_chessboard.use_tools(item_num)
                            my_item_bag.use_tool(item_num)
                            my_chessboard.score = my_chessboard.calc_score()

                elif event.type == pygame.KEYDOWN:
                    keydown_str = sing_player_page.keydown(event)
                    if keydown_str  in ['up','down','right','left']:
                        if keydown_str == 'up':
                            my_chessboard.board, _, _ = my_chessboard.up()
                        if keydown_str == 'down':
                            my_chessboard.board, _, _ = my_chessboard.down()
                        if keydown_str == 'right':
                            my_chessboard.board, _, _ = my_chessboard.right()
                        if keydown_str == 'left':
                            my_chessboard.board, _, _ = my_chessboard.left()
                        my_chessboard.add_new_num()

                        state = my_chessboard.game_state_check()
                        if state:
                            return 'menu'
                        ##TODO 还要写输赢的画面
                        ### 临时生成道具，到时候删
                        if my_chessboard.get_step() % 3 == 0:
                            my_item_bag.add_tool(random.randint(1, 12))
                        ###

                sing_player_page.update(
                    data=my_chessboard.get_board(),
                    score=my_chessboard.score * 100000 + my_chessboard.prizescore,
                    step=my_chessboard.get_step(),
                    item_bag=my_item_bag.get_item_bag(),
                )
                ##

            sing_player_page.show(window)

            pygame.display.flip()

    def _multi_player_page(self, window: pygame.Surface):
        multi_player_page = windows.Multi_player(self.config)
        chessboard1 = chessboard.ChessBoard(
            self.config['window']['chessboard_size'],
        )
        chessboard2 = chessboard.ChessBoard(
            self.config['window']['chessboard_size'],
        )
        chessboard1.score = chessboard1.calc_score()
        item_bag1 = tool.ToolsBag(12)
        item_bag2 = tool.ToolsBag(12)
        item_possible_list = [i for i in range(1, 13)]
        multi_player_page.update(
            data=chessboard1.get_board(),
            score=chessboard1.get_total_score(),
            step=chessboard1.get_step(),
            another_data=chessboard2.get_board(),
            another_score=chessboard2.get_total_score(),
            another_step=chessboard2.get_step(),
            item_bag_num=item_bag1.get_item_bag(),
            another_item_bag_num=item_bag2.get_item_bag(),
        )
        multi_player_page.show(window)
        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                mouse_pos=pygame.mouse.get_pos()
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    onclick_list = multi_player_page.onclick(mouse_pos)
                    if 'surrender' in onclick_list:
                        return 'menu'
                    elif onclick_list != []:
                        if onclick_list[0] in item_possible_list:
                            item_num = onclick_list[0]
                            item_num1=multi_player_page.item_bag.onclick(mouse_pos)
                            if item_num == item_num1:
                                chessboard1.use_tools(item_num)
                                item_bag1.use_tool(item_num)
                                chessboard1.score = chessboard1.calc_score()
                            else:
                                chessboard2.use_tools(item_num)
                                item_bag2.use_tool(item_num)
                                chessboard2.score = chessboard2.calc_score()

                elif event.type == pygame.KEYDOWN:
                    with TimeCounter("keydown"):
                        keydown_str = multi_player_page.keydown(event)
                        for key in keydown_str:
                            if key in ['1-up', '1-down','1-right','1-left']:
                                
                                if key == '1-up':
                                    chessboard1.board, _, _ = chessboard1.up()
                                if key == '1-down':
                                    chessboard1.board, _, _ = chessboard1.down()
                                if key == '1-right':
                                    chessboard1.board, _, _ = chessboard1.right()
                                if key == '1-left':
                                    chessboard1.board, _, _ = chessboard1.left()
                                chessboard1.add_new_num()
                                state = chessboard1.game_state_check()
                                if state:
                                    return 'menu'
                                ##TODO 还要写输赢的画面
                                ### 临时生成道具，到时候删
                                if chessboard1.get_step() % 3 == 0:
                                    item_bag1.add_tool(random.randint(1, 12))
                                ###
                        
                            if key in ['2-up', '2-down','2-right','2-left']:
                                if key == '2-up':
                                    chessboard2.board, _, _ = chessboard2.up()
                                if key == '2-down':
                                    chessboard2.board, _, _ = chessboard2.down()
                                if key == '2-right':
                                    chessboard2.board, _, _ = chessboard2.right()
                                if key == '2-left':
                                    chessboard2.board, _, _ = chessboard2.left()
                                chessboard2.add_new_num()
                                state = chessboard2.game_state_check()
                                if state:
                                    return 'menu'
                                ##TODO 还要写输赢的画面
                                ### 临时生成道具，到时候删
                                if chessboard2.get_step() % 3 == 0:
                                    item_bag2.add_tool(random.randint(1, 12))
                                ###
                multi_player_page.update(
                    data=chessboard1.get_board(),
                    score=chessboard1.get_total_score(),
                    step=chessboard1.get_step(),
                    another_data=chessboard2.get_board(),
                    another_score=chessboard2.get_total_score(),
                    another_step=chessboard2.get_step(),
                    item_bag_num=item_bag1.get_item_bag(),
                    another_item_bag_num=item_bag2.get_item_bag(),
                )
                ##

            multi_player_page.show(window)

            pygame.display.flip()
            
    def _setting_page(self,window:pygame):
        setting_page = windows.Setting(self.config)
        setting_page.show(window)
        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type ==pygame.MOUSEBUTTONDOWN:
                    mouse_pos=pygame.mouse.get_pos()
                    onclick_list,need_to_input=setting_page.onclick(mouse_pos)
                    if setting_page.exit_button in onclick_list:
                        return 'menu'
                    elif setting_page.save_button in onclick_list:
                        setting_page.save(self.config_path)
                        return 'menu'
                    elif need_to_input:
                        setting_page.input_box_list.onclick(mouse_pos)
                elif event.type ==pygame.KEYDOWN:
                    setting_page.input_box_list.keydown(event.key)
                setting_page.show(window)
            pygame.display.flip()
            
                    