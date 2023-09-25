import pygame
import os
from ..tools import Text, Comp_Collection, Button, Chessboard

window_width = 1280  ##之后丢config.json里
window_height = 720


class sing_player:
    def __init__(self,background_img=None,background_color=(0,0,0)):
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
        
        score_str = 'score' + str(self.score)
        self.score_text = Text(
            (window_width // 4, window_height // 8),
            score_str,
        )
        step_str = 'step' + str(self.step)
        self.step_text = Text((window_width * 3 // 4, window_height // 8), step_str)
        # chess=Chessboard((window_width//2,window_height//2),(window_width,window_height))
        self.data = [[0 for _ in range(4)] for _ in range(4)]
        self.chess= Chessboard(
            (window_width // 3, window_height * 5 // 8),
            (window_height * 3 // 4, window_height * 3 // 4),
            len(self.data),
            background_color=(181, 170, 156)
        )
        ai_str = 'AI_clue'
        self.ai_button = Button(
            (window_width * 14 // 16, window_height * 14 // 16), ai_str, size=(200, 50)
        )
        exit_str = 'exit'
        self.exit_button = Button(
            (window_width * 14 // 16, window_height * 15 // 16),
            exit_str,
            size=(200, 50),
            background_color=(255, 255, 255, 100),
        )
        self.pos_item_num = {'del_one_blank': 0, 'double_one_blank': 0, 'c': 0}
        
        self.show_list = Comp_Collection([self.score_text, self.step_text, self.chess, self.ai_button,self.exit_button])

    def show(self, window):
        
        ##道具还没写
        self.chess.update(self.data)
        self.step_text.set_text('step: '+str(self.step))
        self.score_text.set_text('score: '+str(self.score))
        self.show_list.update(window,background_img=self.background_img,background_color=self.background_color)
        
    def onclick(self):
        mouse_pos = pygame.mouse.get_pos()
        onclick_list=self.show_list.onclick(mouse_pos)
        return [part.get_text() for part in onclick_list]
        

    def update(self, data, score, step, item_list=[], item_pos=[]):
        self.data = data
        self.score = score
        self.step = step
        
    def keydown(self,event:pygame.event):
        if event.key in [pygame.K_w,pygame.K_UP]:
            return 'up'
        elif event.key in [pygame.K_a,pygame.K_LEFT]:
            return 'left'
        elif event.key in [pygame.K_s,pygame.K_DOWN]:
            return 'down'
        elif event.key in [pygame.K_d,pygame.K_RIGHT]:
            return 'right'


def main():
    window_width = 1280
    window_height = 720
    data = [[2, 3, 4, 8], [2, 0, 2, 16], [32, 64, 128, 256], [512, 1024, 2048, 4096]]
    window = pygame.display.set_mode((window_width, window_height))
    pygame.init()
    sing_player_page = sing_player(background_img='game\\ui\\src\\img\\menu_bg.jpg')
    # pygame.time.set_timer(pygame.USEREVENT, 5000)
    sing_player_page.update(data, 100, 200)
    sing_player_page.show(window)
    while True:
        for event in pygame.event.get():
           
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                onclick_list=sing_player_page.onclick()
            elif event.type==pygame.KEYDOWN:
                keydown_str=sing_player_page.keydown(event)
                print(keydown_str)
                
        sing_player_page.show(window)