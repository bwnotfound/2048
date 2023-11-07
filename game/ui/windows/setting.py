import pygame
import toml
from .window import Window
from ..tools import Text, Button, InputBox, ComponentGroup


class Setting(Window):
    def __init__(self, config: toml):
        self.config = config
        self.chessboard_size = self.config['window']['sing_player']['chessboard_size']
        self.goal = self.config['window']['sing_player']['goal']
        self.ip_address = self.config['window']['online_player']['ip_address']
        self.port = self.config['window']['online_player']['port']
        self.window_width = self.config['window']['window_width']
        self.window_height = self.config['window']['window_height']
        self.chessboard_size_clue = Text(
            (self.window_width // 3, self.window_height * 3 // 14),
            'sing_player chessboard size',
        )
        self.chessboard_size_button = Button(
            (self.window_width * 2 // 3, self.window_height * 3 // 14),
            str(self.chessboard_size),
        )
        self.goal_text = Text(
            (self.window_width // 3, self.window_height * 5 // 14), 'score goal'
        )
        self.goal_input_box = InputBox(
            (self.window_width * 2 // 3, self.window_height * 5 // 14),
            text=str(self.goal),
        )
        self.online_ip_text = Text(
            (self.window_width // 3, self.window_height * 7 // 14), 'online ip address'
        )
        self.online_ip_input_box = InputBox(
            (self.window_width * 2 // 3, self.window_height * 7 // 14),
            text=str(self.ip_address),
        )
        self.online_port_text = Text(
            (self.window_width // 3, self.window_height * 9 // 14), 'online port'
        )
        self.online_port_input_box = InputBox(
            (self.window_width * 2 // 3, self.window_height * 9 // 14),
            text=str(self.port),
        )

        self.exit_button = Button(
            (self.window_width // 3, self.window_height * 13 // 14), 'exit'
        )
        self.save_button = Button(
            (self.window_width * 2 // 3, self.window_height * 13 // 14), 'save'
        )

        self.show_list = ComponentGroup(
            [
                self.chessboard_size_clue,
                self.chessboard_size_button,
                self.goal_text,
                self.goal_input_box,
                self.online_ip_text,
                self.online_ip_input_box,
                self.online_port_text,
                self.online_port_input_box,
                self.exit_button,
                self.save_button,
            ]
        )

    def show(self, window: pygame.Surface):
        self.show_list.show(window)

    def onclick(self, mouse_pos: (int, int)):
        if self.chessboard_size_button.onclick(mouse_pos):
            self.chessboard_size += 1
            if self.chessboard_size == 7:
                self.chessboard_size = 4
        elif self.goal_input_box.onclick(mouse_pos):
            return self.goal_input_box.onclick(mouse_pos)
        
