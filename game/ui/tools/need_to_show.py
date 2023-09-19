
import pygame

class need_to_show():
    def __init__(self,show_list:list):
        self.show_list=show_list
    
    def show(self,window:pygame.Surface):
        for part in self.show_list:
            if hasattr(part,'show'):
                part.show(window)
    
    def update(self,window:pygame.Surface):
        window.fill((0,0,0))
        for part in self.show_list:
            if hasattr(part,'show'):
                part.show(window)

    def add_compo(self,compo):
        self.show_list.append(compo)
        
    def del_compo(self,compo):
        self.show_list=[i for i in self.show_list if i !=compo]   
        