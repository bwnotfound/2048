import pygame
import socket
import toml
import numpy as np
from .window import Window
from ...net import NetManager
from ..tools import Button,InputBox,Input_box_list,ComponentGroup,Text,Chessboard,Item_bag
from ..tools.common import load_image


class Online_player_ready(Window):
    def __init__(self,config:toml,as_server:bool):
        self.config=config
        self.window_width =self.config['window']['width']
        self.window_height=self.config['window']['height']
        self.background_img = pygame.transform.scale(pygame.image.load(self.config['window']['online_player']['background_img_uri']),(self.window_width,self.window_height))
        self.background_color=(0,0,0)
        if as_server:
            self.ip_address=socket.gethostbyname(socket.gethostname())
        else:
            self.ip_address = self.config['window']['online_player']['ip_address']
        self.port = self.config['window']['online_player']['port']
        self.ip_address_input_box = InputBox(
            (self.window_width // 2, self.window_height * 3 // 14),
            text=str(self.ip_address),
        )
        self.port_input_box = InputBox(
            (self.window_width // 2, self.window_height * 5 // 14),
            text=str(self.port),
        )
        self.exit_button = Button(
            (self.window_width // 2, self.window_height * 13 // 14), 'exit'
        )
        self.connect_button = Button(
            (self.window_width // 2, self.window_height * 11 // 14), 'connect'
        )
        self.component_group=ComponentGroup([self.ip_address_input_box,self.port_input_box,self.exit_button,self.connect_button])
        self.input_box_list=Input_box_list([self.ip_address_input_box,self.port_input_box])
        self.net_manager=NetManager(as_server,self.ip_address,self.port)
        
        
    def show(self, window: pygame.Surface):
        self.component_group.show(window)
        pygame.display.update()
        
    def onclick(self, mouse_pos):
        return [part.get_text() for part in self.component_group.onclick(mouse_pos)]
    
    def connect(self):
        def handle(exception):
            if exception is None:
                print("success")
            else:
                raise exception
        self.net_manager.connect(handle)
    

class Online_player(Window):
    def __init__(self,as_server:bool,ip_address:str,port:int,config:toml,background_color=(0,0,0)):
        self.as_server=as_server
        self.ip_address=ip_address
        self.port=port
        self.net_manager=NetManager(as_server,ip_address,port)
        self.show_error=print
        self.config=config
        self.window_width =self.config['window']['width']
        self.window_height=self.config['window']['height']
        self.background_img = load_image(config['window']['multi_player']['background_img_uri'], (self.window_width, self.window_height))
        self.score = 0
        self.step = 0
        self.background_color=background_color
        
        size=config['window']['chessboard_size']
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
        
        self.item_bag_num = np.zeros(12,int)
        self.item_bag=Item_bag((self.window_width//3,self.window_height*5//27),start_pos=(self.window_width*2//54,self.window_height*20//27))
        self.exit_button = Button(
            (self.window_width * 1 // 5, self.window_height * 26 // 27), exit_str
        )
        
        
        another_score_str = 'score: ' + str(self.another_score)
        self.another_score_text = Text(
            (self.window_width * 7 // 10, self.window_height * 1 // 27), another_score_str
        )
        another_step_str = 'step: ' + str(self.another_step)
        self.another_step_text = Text(
            (self.window_width * 9 // 10, self.window_height * 1 // 27), another_step_str
        )
        # chess=Chessboard((self.window_width//2,self.window_height//2),(self.window_width,self.window_height))
        self.another_chess = Chessboard(
            (self.window_width * 4 // 5, self.window_height * 2 // 3),
            (self.window_width * 9 // 25, self.window_height * 17 // 27),
            len(self.another_data),
            background_color=(181, 170, 156),
        )
        self.another_item_bag_num = np.zeros(12,int)
        self.another_item_bag=Item_bag((self.window_width//3,self.window_height*5//27),start_pos=(self.window_width*34//54,self.window_height*2//27))
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
                self.another_item_bag
            ]
        )
        
    def handle(self, exception):
        if exception is None:
            print("success")
        else:
            raise exception
        pass
    
    def connect(self):
        self.net_manager.connect(self.handle)
    
    def send(self,data):
        self.net_manager.send(data)
        
    def receive(self):
        return self.net_manager.recv()
        