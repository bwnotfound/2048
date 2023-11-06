import toml
import random

import pygame
import numpy as np

from .ui import windows
from .core import *


class Game:
    def __init__(self, config: toml):
        self.config = config
        self.now_page = 'menu'

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
            self.config['window']['sing_player']['chessboard_size'],
            
        )
        my_chessboard.score=my_chessboard.calc_score()
        my_item_bag = tool.ToolsBag(12)
        item_possible_list=[i for i in range(1,13)]
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
                    score=my_chessboard.score*100000+my_chessboard.prizescore,
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
                    elif onclick_list!=[] :
                        if onclick_list[0] in item_possible_list:
                            item_num=onclick_list[0]
                            my_chessboard.use_tools(item_num)
                            my_item_bag.use_tool(item_num)
                            my_chessboard.score=my_chessboard.calc_score()

                elif event.type == pygame.KEYDOWN:
                    keydown_str = sing_player_page.keydown(event)
                    if keydown_str=='up':
                        my_chessboard.board,_,_=my_chessboard.up()
                    if keydown_str=='down':
                        my_chessboard.board,_,_=my_chessboard.down()
                    if keydown_str=='right':
                        my_chessboard.board,_,_=my_chessboard.right()
                    if keydown_str=='left':
                        my_chessboard.board,_,_=my_chessboard.left()
                    my_chessboard.add_new_num()
                    
                    state=my_chessboard.game_state_check()
                    if state:
                        return 'menu'
                    ##TODO 还要写输赢的画面
                    ### 临时生成道具，到时候删
                    if my_chessboard.get_step()%3==0:
                        my_item_bag.add_tool(random.randint(1,12))
                    ###
                
                sing_player_page.update(
                    data=my_chessboard.get_board(),
                    score=my_chessboard.score*100000+my_chessboard.prizescore,
                    step=my_chessboard.get_step(),
                    item_bag=my_item_bag.get_item_bag(),
                ) 
                ##

            sing_player_page.show(window)
            
            pygame.display.flip()
