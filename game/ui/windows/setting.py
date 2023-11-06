import pygame
import toml
from .window import Window
from ..tools import Text,Button

class Setting(Window):
    def __init__(self,config:toml,window:pygame.Surface):
        self.config=config
        self.window_width=self.config['window']['window_width']
        self.window_height=self.config['window']['window_height']
        self.sing_player_chessboard_size_clue=Text((self.window_width//3,self.window_height*3//14),'sing_player chessboard size')
        self.sing_player_chessboard_size_button=Button((self.window_width*2//3,self.window_height*3/14),str(self.config['window']['sing_player']['chessboard_size']))
        