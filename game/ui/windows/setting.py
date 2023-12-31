import pygame
import toml
from .window import Window
from ..tools import Text, Button, InputBox, ComponentGroup, Input_box_list
from .page import BasePage
from .page_manager import PageManager


class Setting(Window, BasePage):
    def __init__(
        self,
        page_man: PageManager,
        config: toml,
    ):
        super(BasePage, self).__init__()
        self.page_man = page_man
        self.config = config
        self.config_path = config['config_path']
        self.chessboard_size = self.config['window']['chessboard_size']
        self.goal = self.config['window']['sing_player']['goal']
        self.ip_address = self.config['window']['online_player']['ip_address']
        self.port = self.config['window']['online_player']['port']
        self.window_width = self.config['window']['width']
        self.window_height = self.config['window']['height']
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

        self.component_group = ComponentGroup(
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

        self.input_box_list = Input_box_list(
            [
                self.online_ip_input_box,
                self.online_port_input_box,
                self.goal_input_box,
            ]
        )

    def show(self, window: pygame.Surface):
        window.fill((125, 125, 125))
        self.component_group.show(window)

    def onclick(self, mouse_pos: (int, int)):
        onclick_list = self.component_group.onclick(mouse_pos)
        if self.chessboard_size_button in onclick_list:
            self.chessboard_size += 1
            if self.chessboard_size == 7:
                self.chessboard_size = 4
            self.chessboard_size_button.set_text(str(self.chessboard_size))
        if (
            self.goal_input_box
            or self.online_ip_input_box
            or self.online_port_input_box in onclick_list
        ):
            input_box_onclicked = self.input_box_list.onclick(mouse_pos)
        return onclick_list, input_box_onclicked

    def run(self, event: pygame.event.Event):
        if event is None:
            pass
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            onclick_list, need_to_input = self.onclick(mouse_pos)
            if self.exit_button in onclick_list:
                self.page_man.del_page(self)
            elif self.save_button in onclick_list:
                self.save(self.config_path)
                self.page_man.del_page(self)
            elif need_to_input:
                self.input_box_list.onclick(mouse_pos)
        elif event.type == pygame.KEYDOWN:
            self.input_box_list.keydown(event.key)

    def save(self, config_path: str):
        self.config['window']['sing_player']['chessboard_size'] = self.chessboard_size
        self.config['window']['sing_player']['goal'] = int(self.goal_input_box.text)
        self.config['window']['online_player'][
            'ip_address'
        ] = self.online_ip_input_box.text
        self.config['window']['online_player']['port'] = int(
            self.online_port_input_box.text
        )
        with open(config_path, 'w') as f:
            toml.dump(self.config, f)
