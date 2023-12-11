import toml
from time import perf_counter, sleep
import pygame

from .ui.windows.page_manager import PageManager


class Clock:
    def __init__(self):
        self.tick_last_time = 0

    def is_ready(self, fps):
        now = perf_counter()
        if now - self.tick_last_time >= 1 / fps:
            self.tick_last_time = now
            return True
        return False

    def tick(self, fps):
        while not self.is_ready(fps):
            sleep(max(0, 1 / fps - (perf_counter() - self.tick_last_time)))


class GameManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        config = toml.load(config_path)
        config['config_path'] = config_path
        self.config = config
        self.skip_rest_event = False
        self.close_flag = False
        self.page_man = PageManager()

    @property
    def width(self):
        return self.window.get_width()

    @property
    def height(self):
        return self.window.get_height()

    def close(self):
        self.close_flag = True

    def new_menu(self):
        from .ui.windows.menu import Menu

        return Menu(
            self.page_man,
            self.config,
            pygame.Rect(0, 0, self.width, self.height),
            background_img=self.config['window']['menu']['background_img_uri'],
            menu_font=self.config['window']['menu']['menu_font_uri'],
        )

    def start(self):
        self.window_width = self.config['window']['width']
        self.window_height = self.config['window']['height']
        self.window = window = pygame.display.set_mode(
            (self.window_width, self.window_height)
        )
        pygame.init()

        render_clock = Clock()
        run_clock = Clock()
        while True and not self.close_flag:
            render_clock.tick(240)
            if len(self.page_man.get_page_list()) == 0:
                self.page_man.add_page(self.new_menu())
            for page in self.page_man.get_page_list():
                page.show(window)
            pygame.display.flip()
            if not run_clock.is_ready(60):
                continue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if self.skip_rest_event:
                    self.skip_rest_event = False
                    break
                for page in self.page_man.get_page_list():
                    page.run(event)
            else:
                for page in self.page_man.get_page_list():
                    page.run(None)
