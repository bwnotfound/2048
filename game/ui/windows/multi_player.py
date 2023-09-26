import pygame
import os
from ..tools import Text, ComponentGroup, Button, Chessboard

window_width = 1280  ##之后丢config.json里
window_height = 720


class multi_player:
    def __init__(self, background_img=None, background_color=(0, 0, 0)):
        if background_img != None:
            if not os.path.exists(background_img):
                print(f'img {background_img} not exists')
            else:
                image = pygame.image.load(background_img)
                self.background_img = pygame.transform.scale(
                    image, (window_width, window_height)
                )
        else:
            self.background_img = None
        self.background_color = background_color

        self.score = 0
        self.step = 0
        self.data = [[0 for _ in range(4)] for _ in range(4)]
        self.pos_item_num = {'del_one_blank': 0, 'double_one_blank': 0, 'c': 0}

        self.another_score = 0
        self.another_step = 0
        self.another_data = [[0 for _ in range(4)] for _ in range(4)]
        self.another_pos_item_num = {'del_one_blank': 0, 'double_one_blank': 0, 'c': 0}

        exit_str = 'surrender'
        score_str = 'score: ' + str(self.score)
        self.score_text = Text(
            (window_width * 1 // 5, window_height * 19 // 27), score_str
        )

        step_str = 'step: ' + str(self.step)
        self.step_text = Text(
            (window_width * 1 // 5, window_height * 21 // 27), step_str
        )
        self.chess = Chessboard(
            (window_width // 5, window_height // 3),
            (window_width * 9 // 25, window_height * 17 // 27),
            len(self.data),
            background_color=(181, 170, 156),
        )
        self.exit_button = Button(
            (window_width * 1 // 5, window_height * 26 // 27), exit_str
        )
        another_score_str = 'score: ' + str(self.another_score)
        self.another_score_text = Text(
            (window_width * 4 // 5, window_height * 1 // 27), another_score_str
        )
        another_step_str = 'step: ' + str(self.another_step)
        self.another_step_text = Text(
            (window_width * 4 // 5, window_height * 3 // 27), another_step_str
        )
        # chess=Chessboard((window_width//2,window_height//2),(window_width,window_height))
        self.another_chess = Chessboard(
            (window_width * 4 // 5, window_height * 2 // 3),
            (window_width * 9 // 25, window_height * 17 // 27),
            len(self.another_data),
            background_color=(181, 170, 156),
        )
        ##道具还没写
        self.another_exit_button = Button(
            (window_width * 4 // 5, window_height * 8 // 27),
            exit_str,
            border_color=(100, 100, 100, 100),
            border_radius=20,
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
            ]
        )

    def show(self, window: pygame.Surface):
        if self.background_img != None:
            window.blit(self.background_img, (0, 0))
        else:
            window.fill(self.background_color)
        ##道具还没写
        self.show_list.update(window, background_img=self.background_img)

    def onclick(self):
        mouse_pos = pygame.mouse.get_pos()
        return [part.get_text() for part in self.show_list.onclick(mouse_pos)]

    def keydown(self, event: pygame.event):
        if event.key in [pygame.K_w, pygame.K_UP]:
            return 'up'
        elif event.key in [pygame.K_a, pygame.K_LEFT]:
            return 'left'
        elif event.key in [pygame.K_s, pygame.K_DOWN]:
            return 'down'
        elif event.key in [pygame.K_d, pygame.K_RIGHT]:
            return 'right'

    def update(
        self,
        data,
        score,
        step,
        another_data,
        another_score,
        another_step,
        item_list=[],
        item_pos=[],
        another_item_list=[],
        another_item_pos=[],
    ):
        self.data = data
        self.score = score
        self.step = step
        self.another_data = another_data
        self.another_score = another_score
        self.another_step = another_step


def main():
    window_width = 1280
    window_height = 720
    data = [[2, 3, 4, 8], [2, 0, 2, 16], [32, 64, 128, 256], [512, 1024, 2048, 4096]]
    another_data = [
        [2, 3, 4, 8],
        [2, 0, 2, 16],
        [512, 1024, 2048, 4096],
        [32, 64, 128, 256],
    ]
    window = pygame.display.set_mode((window_width, window_height))
    pygame.init()
    multi_player_page = multi_player(background_img='game\\ui\\src\\img\\multi_bg.jpg')
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
