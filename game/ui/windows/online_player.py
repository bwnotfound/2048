import threading
import time

import pygame
import toml
from .window import Window
from ...net import NetManager
from ..tools import (
    Button,
    ComponentGroup,
    Text,
)
from ..tools.common import load_image
from .page import BasePage
from .page_manager import PageManager
from .multi_player import MultiPlayer


class OnlineChoice(Window, BasePage):
    def __init__(self, page_man: PageManager, config: toml):
        Window.__init__(self)
        BasePage.__init__(self)
        self.page_man = page_man
        self.config = config
        self.window_width = self.config['window']['width']
        self.window_height = self.config['window']['height']
        self.background_img = pygame.transform.scale(
            pygame.image.load(
                self.config['window']['online_player']['background_img_uri']
            ),
            (self.window_width, self.window_height),
        )
        self.background_color = (0, 0, 0)
        self.server_button = Button(
            (self.window_width // 2, self.window_height * 5 // 14), 'as_server'
        )
        self.client_button = Button(
            (self.window_width // 2, self.window_height * 7 // 14), 'as_client'
        )
        self.exit_button = Button(
            (self.window_width // 2, self.window_height * 13 // 14), 'exit'
        )
        self.component_group = ComponentGroup(
            [
                self.server_button,
                self.client_button,
                self.exit_button,
            ]
        )
        self.pages = []

    def show(self, window: pygame.Surface):
        if self.visible and len(self.pages) == 0:
            self.component_group.update(window, background_img=self.background_img)
        for page in self.pages:
            page.show(window)

    def onclick(self, mouse_pos):
        return [part.get_text() for part in self.component_group.onclick(mouse_pos)]

    def get_page(self, page):
        if page in self.pages:
            return page
        return None

    def add_page(self, page):
        if self.get_page(page) is None:
            self.pages.append(page)

    def remove_page(self, page):
        if page in self.pages:
            self.pages.remove(page)

    def run(self, event: pygame.event.Event):
        if event is None:
            pass
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            onclick_list = self.onclick(mouse_pos)
            if 'as_server' in onclick_list:
                self.page_man.add_page(
                    OnlineWaitWindow(self.page_man, True, self.config)
                )
                self.page_man.del_page(self)
            elif 'as_client' in onclick_list:
                self.page_man.add_page(
                    OnlineWaitWindow(self.page_man, False, self.config)
                )
                self.page_man.del_page(self)
            elif 'exit' in onclick_list:
                while len(self.pages) > 0:
                    self.pages.pop().close()
                self.close()
        for page in self.pages:
            page.run(event)


class OnlineWaitWindow(Window, BasePage):
    def __init__(
        self,
        page_man: PageManager,
        as_server: bool,
        config: toml,
        background_color=(0, 0, 0),
    ):
        super().__init__()
        self.page_man = page_man
        self.as_server = as_server
        self.net_manager = NetManager(as_server)
        self.config = config
        self.window_width = self.config['window']['width']
        self.window_height = self.config['window']['height']
        self.background_img = load_image(
            config['window']['multi_player']['background_img_uri'],
            (self.window_width, self.window_height),
        )
        self.background_color = background_color

        self.info_length = 5
        self.text_list = [
            Text(
                (self.window_width * 2 // 5, self.window_height * (5 + 2 * i) // 16),
                "Test",
                font_color=(150, 200, 165),
                font_size=30,
            )
            for i in range(self.info_length)
        ]
        for text in self.text_list:
            text.visible = False
        self.btn_list = [
            Button(
                (self.window_width * 4 // 5, self.window_height * (5 + 2 * i) // 16),
                f'connect to {i+1}-th server',
            )
            for i in range(self.info_length)
        ]
        for btn in self.btn_list:
            btn.visible = False

        self.top_text = Text(
            (self.window_width // 2, self.window_height * 1 // 16),
            "Waiting for connection...",
            font_color=(150, 200, 165),
        )
        self.top_text.visible = False

        self.show_list = ComponentGroup(
            self.text_list + self.btn_list + [self.top_text]
        )
        self.listened_address = []  # (last_time, address, data)
        self.pre_show_info = []
        self.connecting = False

        if self.as_server:
            self.broadcast_close_event = threading.Event()
            _BroadcastThread(self.net_manager, self.broadcast_close_event).start()
            self.net_manager.connect(self.server_connection)
        else:
            self.listen_close_event = threading.Event()
            self.listened_list_lock = threading.Lock()
            _ListenThread(
                self.net_manager,
                self.listened_address,
                self.listened_list_lock,
                self.listen_close_event,
            ).start()

        if as_server:
            self.top_text.visible = True
            self.top_text.set_text("Waiting for connection...")

    def server_connection(self, exception):
        if exception is None:
            print("success from server.")
            self.page_man.add_page(
                MultiPlayer(
                    self.page_man,
                    self.as_server,
                    self.net_manager,
                    self.config,
                )
            )
            self.page_man.del_page(self)
        else:
            raise exception
        pass

    def client_connection(self, exception):
        if exception is None:
            print(
                "success from client. connect to {}:{}".format(
                    self.client_net_manager.host, self.client_net_manager.port
                )
            )
            self.page_man.add_page(
                MultiPlayer(
                    self.page_man,
                    self.as_server,
                    self.client_net_manager,
                    self.config,
                )
            )
            self.page_man.del_page(self)
        else:
            raise exception
        pass

    def connect_server(self, address):
        self.client_net_manager = NetManager(False, *address)
        self.client_net_manager.connect(self.client_connection)

    def send(self, data):
        self.net_manager.send(data)

    def receive(self):
        return self.net_manager.recv()

    def show(self, window: pygame.Surface):
        self.show_list.update(
            window,
            background_img=self.background_img,
            background_color=self.background_color,
        )

    def onclick(self, mouse_pos):
        return [part.get_text() for part in self.show_list.onclick(mouse_pos)]

    def update(self):
        pass

    def close(self):
        if self.as_server:
            self.broadcast_close_event.set()
        else:
            self.listen_close_event.set()
        self.page_man.del_page(self)

    def show_client_window(self):
        self.pre_show_info = []
        for i, t in enumerate(self.listened_address):
            if i > self.info_length:
                break
            address, msg = (t[1][0], t[1][1]), t[2]
            msg = f"{address[0]}:{address[1]}|{msg}"
            self.pre_show_info.append((address, msg))
        i = 0
        for i, item in enumerate(self.pre_show_info):
            address, msg = item
            self.text_list[i].set_text(msg)
            self.text_list[i].visible = True
            self.btn_list[i].visible = True
        for j in range(i + 1, self.info_length):
            self.text_list[j].visible = False
            self.btn_list[j].visible = False

    def run(self, event: pygame.event.Event):
        if event is None:
            pass
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            onclick_list = self.onclick(mouse_pos)
            if 'exit' in onclick_list:
                self.close()
            if len(onclick_list) == 1 and len(self.pre_show_info) > 0:
                text = onclick_list[0]
                try:
                    i = (
                        int(text[len("connect to ") : len(text) - len("-th server")])
                        - 1
                    )
                    address = self.pre_show_info[i][0]
                    self.connect_server(address)
                    self.connecting = True
                except ValueError:
                    pass
        if not self.as_server:
            self.show_client_window()
            if len(self.pre_show_info) == 0:
                self.top_text.visible = True
                self.top_text.set_text("Searching server...")
            if self.connecting:
                self.top_text.visible = True
                self.top_text.set_text("Connecting...")


class _BroadcastThread(threading.Thread):
    def __init__(self, net_manager: NetManager, close_event: threading.Event):
        super().__init__()
        self.net_manager = net_manager
        self.close_event = close_event

    def run(self):
        while not self.close_event.is_set():
            self.net_manager.broadcast('Message from server')
            time.sleep(0.5)


class _ListenThread(threading.Thread):
    def __init__(
        self,
        net_manager: NetManager,
        listened_address: list,
        lock: threading.Lock,
        close_event: threading.Event,
        timeout=3,
    ):
        super().__init__()
        self.net_manager = net_manager
        self.listened_address = listened_address
        self.lock = lock
        self.close_event = close_event
        self.timeout = timeout

    def run(self):
        while not self.close_event.is_set():
            recv_address, recv_data = self.net_manager.recv_broadcast()
            self.lock.acquire()
            for i, (last_time, address, data) in enumerate(self.listened_address):
                if address[0] != address[0] or address[1] != address[1]:
                    continue
                self.listened_address[i] = (time.perf_counter(), address, recv_data)
                break
            else:
                self.listened_address.append(
                    (time.perf_counter(), recv_address, recv_data)
                )
            listened_address = [
                (last_time, address, data)
                for last_time, address, data in self.listened_address
                if time.perf_counter() - last_time <= self.timeout
            ]
            self.listened_address.clear()
            self.listened_address.extend(listened_address)
            self.lock.release()
