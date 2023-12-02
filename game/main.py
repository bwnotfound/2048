import toml

import pygame


class GameManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        config = toml.load(config_path)
        self.config = config
        self.skip_rest_event = False
        self.close_flag = False

    @property
    def width(self):
        return self.window.get_width()

    @property
    def height(self):
        return self.window.get_height()
    
    def close(self):
        self.close_flag = True

    def start(self):
        self.window_width = self.config['window']['width']
        self.window_height = self.config['window']['height']
        self.window = window = pygame.display.set_mode(
            (self.window_width, self.window_height)
        )
        pygame.init()

        from .ui.windows.menu import Menu

        self.menu = Menu(
            self,
            pygame.Rect(0, 0, self.width, self.height),
            background_img=self.config['window']['menu']['background_img_uri'],
            menu_font=self.config['window']['menu']['menu_font_uri'],
        )
        clock = pygame.time.Clock()
        while True and not self.close_flag:
            self.menu.show(window)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if self.skip_rest_event:
                    self.skip_rest_event = False
                    break
                self.menu.run(event)
            else:
                self.menu.run(None)
            clock.tick(60)
