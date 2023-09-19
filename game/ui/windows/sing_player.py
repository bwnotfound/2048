import pygame
from ..tools import text,need_to_show,button,chessboard

window_width=1280##之后丢config.json里
window_height=720
class sing_player():
    
    def __init__(self):
       
        
        self.score=0
        self.step=0
        self.data=[[0 for _ in range(4)] for _ in range(4)]
        self.pos_item_num={'del_one_blank':0,'double_one_blank':0,'c':0}
        
    def show(self,window):
        score_str='score'+str(self.score)
        score_text=text((window_width//4,window_height//8),score_str)
        step_str='step'+str(self.step)
        step_text=text((window_width*3//4,window_height//8),step_str)
        chess=chessboard((window_width//3,window_height*5//8),(window_height*3//4,window_height*3//4),len(self.data))
        ##道具还没写
        ai_str='AI提示'
        ai_button=button((window_width*15//16,window_height*14//16),ai_str)
        exit_str='退出'
        exit_button=button((window_width*15//16,window_height*15//16),exit_str)
        show_list=need_to_show([score_text,step_text,chess,ai_button,exit_button])
        show_list.update(window)
        
    def update(self,data,score,step,item_list=[],item_pos=[]):
        self.data=data
        self.score=score
        self.step=step
        
        
def main():
    window_width =  1280
    window_height = 720
    data=[
        [2,3,4,8],
        [2,0,2,16],
        [32,64,128,256],
        [512,1024,2048,4096]
    ]
    window=pygame.display.set_mode((window_width,window_height))
    pygame.init()
    sing_player_page=sing_player()
    # pygame.time.set_timer(pygame.USEREVENT, 5000)
    sing_player_page.update(data,100,200)
    sing_player_page.show(window)
    pygame.display.flip()
    while(True):
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                pygame.quit()
                exit()
