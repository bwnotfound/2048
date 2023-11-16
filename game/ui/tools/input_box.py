import pygame
import time
from .common import abstract_onclick_comp,abstract_show_comp


class InputBox(pygame.sprite.Sprite, abstract_onclick_comp,abstract_show_comp):
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
            if self.ready == True:
                return True
            elif self.ready == False:
                self.ready = True
                self.text_show = self.text_font.render(self.text + self.underline, True, self.click_color)
                return True
        else:
            if self.ready == True:
                self.ready = False
                self.text_show = self.text_font.render(self.text + self.underline, True, self.color)
                return True
            elif self.ready == False:
                return False
         
    def keydown(self,key):
        if self.ready:
            if key==pygame.K_BACKSPACE:
                self.del_text()
            elif key==pygame.K_RETURN:
                self.ready=False
            elif key==pygame.K_ESCAPE:
                self.ready=False
            else:
                self.add_text(pygame.key.name(key))
                
        
        
    def in_rect(self,mouse_pos):
        if self.rect.left < mouse_pos[0] < self.rect.right and self.rect.top < mouse_pos[1] < self.rect.bottom:
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


class Input_box_list(abstract_onclick_comp):
    def __init__(self,input_box_list:list[InputBox]):
        super().__init__()
        self.input_box_list=input_box_list
        self.has_ready=None
        
    def onclick(self, mouse_pos):
        for input_box in self.input_box_list:
            if input_box.onclick(mouse_pos):
                self.has_ready=input_box
                return True
        return False
    
    def add_text(self,text:str):
        if self.has_ready!=None:
            self.has_ready.add_text(text)
            
    def del_text(self, del_num=1):
        if self.has_ready!=None:
            self.has_ready.del_text(del_num)
            
    def add_input_box(self,input_box:InputBox):
        self.input_box_list.append(input_box)
        
    def del_input_box(self,input_box:InputBox):
        self.input_box_list=[part for part in self.input_box_list if part!=input_box]
        
    def get_text(self):
        return [part.get_text() for part in self.input_box_list]
    
    def keydown(self,key):
        if self.has_ready!=None:
            self.has_ready.keydown(key)