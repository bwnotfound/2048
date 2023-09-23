
import pygame

class Need_to_show():
    def __init__(self,show_list:list):
        self.show_list=show_list
    
    def show(self,window:pygame.Surface):
        for part in self.show_list:
            if hasattr(part,'show'):
                part.show(window)
    
    def update(self,window:pygame.Surface,bg_img=None,bgc=(0,0,0)):
        if bg_img==None:
            window.fill(bgc)
        else:
            window.blit(bg_img,(0,0))
        for part in self.show_list:
            if hasattr(part,'show'):
                part.show(window)
        pygame.display.flip()

    def add_compo(self,compo):
        self.show_list.append(compo)
        
    def del_compo(self,compo):
        self.show_list=[i for i in self.show_list if i !=compo]   
        