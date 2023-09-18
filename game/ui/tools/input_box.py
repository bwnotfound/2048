import pygame

class input_box():
    def __init__(self,center,char_num=-1,color=(100,100,100),size=60,font=None):
        self.center=center
        self.char_num=char_num
        self.color=color
        self.click_color=tuple(x*1.5 if x<170 else 255 for x in self.color)
        self.size=size
        self.font=font
        self.text=''
        self.underline='_'
        self.ready=False
        
    def show(self,window:pygame.Surface):
        text_font=pygame.font.Font(self.font,self.size)
        if self.text!='':
            self.underline=''
        else:
            self.underline='_'
        text_show=text_font.render(self.text+self.underline,True,self.click_color) if self.ready else text_font.render(self.text+self.underline,True,self.color)
        rect=text_show.get_rect()
        rect.center=self.center
        window.blit(text_show,rect)
        
    def onclick(self,mouse_pos):
        text_font=pygame.font.Font(self.font,self.size)
        text_show=text_font.render(self.text,True,self.color)
        rect=text_show.get_rect()   
        rect.center=self.center
        if mouse_pos[0]>rect.x-30 and mouse_pos[0]<rect.x+30+rect.width and mouse_pos[1]>rect.y-30 and mouse_pos[1]<rect.y+rect.height+30:
            self.ready=True
            return True
        else:
            self.ready=False
            return False
        
    def add_text(self,text:str):
        self.text=self.text+text
        
    def del_text(self,del_num=1):
        if len(self.text)>del_num:  
            self.text=self.text[:0-del_num]
        else: self.text=''
    
    def get_text(self):
        return self.text
    
    def is_ready(self):
        return self.ready