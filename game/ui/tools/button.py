import pygame
import os

class button():
    def __init__(self,center,title_text='text',title_size=60,color=(150,150,150),size=None,font=None):
        self.center=center
        self.title_text=title_text
        self.title_size=title_size
        if font==None or font in pygame.font.get_fonts():
            self.font=pygame.font.SysFont(font,title_size)
        elif not os.path.exists(font):
            print(f'font \'{font}\' not exists')
            self.font=pygame.font.SysFont(None,title_size)
        else:
            self.font=pygame.font.Font(font,title_size)    
        self.color=color
        if size==None:
            self.size=self.font.render(self.title_text,True,self.color).get_size()
        else:
            self.size=size
            
        
    def show(self,window:pygame.Surface):
        text_show=self.font.render(self.title_text,True,self.color)
        rect=text_show.get_rect()
        rect.center=self.center
        window.blit(text_show,rect)
    def onclick(self,mouse_pos):
        if mouse_pos[0]>self.center[0]-self.size[0]/2 and mouse_pos[0]<self.center[0]+self.size[0]/2 and mouse_pos[1]>self.center[1]-self.size[1]/2 and mouse_pos[1]<self.center[1]+self.size[1]/2:
            return True
        else:
            return False
    
    def setTitle(self,title_text:str):
        self.title_text=title_text
    def setColor(self,color):
        self.color=color