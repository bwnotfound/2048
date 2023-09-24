import pygame
import os
from ..tools import Text, Need_to_show, Button, Chessboard

window_width = 1280  ##之后丢config.json里
window_height = 720


class multi_player:
    def __init__(self, bg_img=None, background_color=(0, 0, 0)):
        if bg_img != None:
            if not os.path.exists(bg_img):
                print(f'img {bg_img} not exists')
            else:
                image = pygame.image.load(bg_img)
                self.bg_img = pygame.transform.scale(
                    image, (window_width, window_height)
                )
        else:
            self.bg_img = None
        self.background_color = background_color

        self.score = 0
        self.step = 0
        self.data = [[0 for _ in range(4)] for _ in range(4)]
        self.pos_item_num = {'del_one_blank': 0, 'double_one_blank': 0, 'c': 0}

        self.another_score = 0
        self.another_step = 0
        self.another_data = [[0 for _ in range(4)] for _ in range(4)]
        self.another_pos_item_num = {'del_one_blank': 0, 'double_one_blank': 0, 'c': 0}

    def show(self, window: pygame.Surface):
        if self.bg_img != None:
            window.blit(self.bg_img, (0, 0))
        else:
            window.fill(self.background_color)
        score_str = 'score: ' + str(self.score)
        score_text = Text((window_width * 1 // 5, window_height * 19 // 27), score_str)
        step_str = 'step: ' + str(self.step)
        step_text = Text((window_width * 1 // 5, window_height * 21 // 27), step_str)
        # chess=Chessboard((window_width//2,window_height//2),(window_width,window_height))
        chess = Chessboard(
            (window_width // 5, window_height // 3),
            (window_width * 9 // 25, window_height * 17 // 27),
            len(self.data),
            background_color=(181, 170, 156),
        )
        chess.update(self.data)
        ##道具还没写
        exit_str = 'I Loss'
        exit_button = Button(
            (window_width * 1 // 5, window_height * 26 // 27), exit_str
        )
        show_list = Need_to_show([score_text, step_text, chess, exit_button])

        another_score_str = 'score: ' + str(self.another_score)
        another_score_text = Text(
            (window_width * 4 // 5, window_height * 1 // 27), another_score_str
        )
        another_step_str = 'step: ' + str(self.another_step)
        another_step_text = Text(
            (window_width * 4 // 5, window_height * 3 // 27), another_step_str
        )
        # chess=Chessboard((window_width//2,window_height//2),(window_width,window_height))
        another_chess = Chessboard(
            (window_width * 4 // 5, window_height * 2 // 3),
            (window_width * 9 // 25, window_height * 17 // 27),
            len(self.another_data),
            background_color=(181, 170, 156),
        )
        another_chess.update(self.another_data)
        ##道具还没写
        another_exit_button = Button(
            (window_width * 4 // 5, window_height * 8 // 27),
            exit_str,
            border_color=(100, 100, 100, 100),
            border_radius=20,
        )
        show_list = Need_to_show(
            [
                score_text,
                step_text,
                chess,
                exit_button,
                another_score_text,
                another_step_text,
                another_chess,
                another_exit_button,
            ]
        )
        show_list.update(window, bg_img=self.bg_img)

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
    multi_player_page = multi_player(bg_img='game\\ui\\src\\img\\multi_bg.jpg')
    # pygame.time.set_timer(pygame.USEREVENT, 5000)
    multi_player_page.update(data, 100, 200, another_data, 150, 250)
    multi_player_page.show(window)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
