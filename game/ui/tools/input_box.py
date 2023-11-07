import pygame
import time
from .common import abstract_onclick_comp


class InputBox(pygame.sprite.Sprite, abstract_onclick_comp):
    def __init__(self, center, text=None, color=(100, 100, 100), size=60, font=None):
        self.center = center
        self.color = color
        self.click_color = tuple(x * 1.5 if x < 170 else 255 for x in self.color)
        self.size = size
        self.font = font
        self.text = '' if text == None else text
        self.underline = '_'
        self.ready = False
        self.text_font = pygame.font.Font(self.font, self.size)
        if self.text != '':
            self.underline = ''
        else:
            self.underline = '_'
        self.text_show = (
            self.text_font.render(self.text + self.underline, True, self.click_color)
            if self.ready
            else self.text_font.render(self.text + self.underline, True, self.color)
        )
        self.rect = self.text_show.get_rect()
        self.rect.center = self.center
        
    def show(self, window: pygame.Surface):
        window.blit(self.text_show, self.rect)

    def onclick(self, mouse_pos):
        if self.in_rect(mouse_pos):
            self.ready = True
            self.input_text()
        else:
            self.ready = False
            
    def input_text(self):
        last_time=time.time()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos=pygame.mouse.get_pos()
                    if not self.in_rect(mouse_pos):
                        return
                elif event.type == pygame.KEYDOWN:
                    if time.time()-last_time>0.15:
                        last_time=time.time()
                        if event.key==pygame.K_BACKSPACE:
                            if self.is_ready()==True:
                                self.del_text() 
                        elif pygame.K_0 <=event.key<=pygame.K_9:
                            if self.is_ready()==True:
                                self.add_text(str(event.key-pygame.K_0))
                        elif pygame.K_PERIOD==event.key:
                            if self.is_ready()==True:
                                self.add_text('.')
                        self.show()
        
    def in_rect(self,mouse_pos):
        if (
            mouse_pos[0] > self.rect.x - 30
            and mouse_pos[0] < self.rect.x + 30 + self.rect.width
            and mouse_pos[1] > self.rect.y - 30
            and mouse_pos[1] < self.rect.y + self.rect.height + 30
        ):
            return True
        else:
            return False
        

    def add_text(self, text: str):
        self.text = self.text + text
        self.text_show = (
            self.text_font.render(self.text + self.underline, True, self.click_color)
            if self.ready
            else self.text_font.render(self.text + self.underline, True, self.color)
        )
        self.rect = self.text_show.get_rect()
        self.rect.center = self.center

    def del_text(self, del_num=1):
        if len(self.text) > del_num:
            self.text = self.text[: 0 - del_num]
        else:
            self.text = ''
            
        self.text_show = (
            self.text_font.render(self.text + self.underline, True, self.click_color)
            if self.ready
            else self.text_font.render(self.text + self.underline, True, self.color)
        )
        self.rect = self.text_show.get_rect()
        self.rect.center = self.center

    def get_text(self):
        return self.text

    def is_ready(self):
        return self.ready
