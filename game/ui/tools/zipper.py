import pygame

class zipper():
    def __init__(self,pos,length,mouse_percent=0.5,data_range=(0,100),font=None):
        self.pos=pos
        self.length=length
        self.mouse_percent=mouse_percent
        self.data_range=data_range
        self.font=font
    
    def show(self,window:pygame.Surface):
        font=pygame.font.Font(self.font,20)
        num=int(self.mouse_percent*(self.data_range[1]-self.data_range[0]))
        title=font.render(str(num),True,(150,150,150))
        title_rect=title.get_rect()
        title_rect.center=(self.pos[0]+self.length/2,self.pos[1]+10)
        window.blit(title,title_rect)
        pygame.draw.line(window,(103,157,180),(self.pos[0],self.pos[1]+30),(self.pos[0]+self.length,self.pos[1]+30),width=5)
        pygame.draw.line(window,(169,220,219),(self.pos[0]+self.mouse_percent*self.length,self.pos[1]+23),(self.pos[0]+self.mouse_percent*self.length,self.pos[1]+37),width=10)
        
    def onclick(self,mouse_pos):
        if mouse_pos[0]>self.pos[0] and mouse_pos[0]<self.pos[0]+self.length and mouse_pos[1]>self.pos[1]+20 and mouse_pos[1]<self.pos[1]+40:
            self.mouse_percent=(mouse_pos[0]-self.pos[0])/self.length
            return True
        else:
            return False
        
    def getNum(self):
        return int(self.mouse_percent*(self.data_range[1]-self.data_range[0]))
        