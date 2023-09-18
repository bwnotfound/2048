import pygame

class text():
    def __init__(self,center,text,color=(255,255,255),size=60,font=None):
        self.center=center
        self.text=text
        self.color=color
        self.size=size
        self.font=font
    def show(self,window:pygame.Surface):
        text_font=pygame.font.Font(self.font,self.size)
        text_show=text_font.render(self.text,True,self.color)
        rect=text_show.get_rect()
        rect.center=self.center
        window.blit(text_show,rect)
    def set_text(self,text:str):
        self.text=text