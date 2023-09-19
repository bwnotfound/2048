from .text import Text
import pygame

color_dict={0:(100,100,100),3: (33, 26, 40), 2: (3, 91, 83), 4: (167, 223, 145), 8: (113, 70, 124), 16: (164, 240, 213), 32: (56, 221, 16), 64: (15, 7, 86), 128: (216, 48, 126), 256: (149, 57, 41), 512: (159, 13, 43), 1024: (88, 102, 177), 2048: (168, 87, 113), 4096: (162, 245, 251), 8192: (52, 67, 88), 16384: (186, 176, 230)}

class chessboard():
    def __init__(self,center,size,row_num=4,background_color=(0,0,0)):
        self.center=center
        self.size=size
        self.row_num=row_num
        self.bgc=background_color
        self.data=[[0 for _ in range(row_num)] for _ in range(row_num)]

    def _show_part(self,center,value,width,height,window):
        rect=pygame.Rect(center[0]-width//2,center[1]-height//2,width,height)
        color=color_dict[value]
        show_text=Text(center,str(value),font_size=int((width+height)//6))
        pygame.draw.rect(window,color,rect)
        if value!=0:
            show_text.show(window)
        
    def show(self,window):
        rect=pygame.Rect(self.center[0]-self.size[0]//2,self.center[1]-self.size[1]//2,self.size[0],self.size[1])
        pygame.draw.rect(window,self.bgc,rect)
        for i in range(self.row_num):
            for j in range(self.row_num):
                if self.data[i][j] in color_dict.keys():
                    self._show_part((self.center[0]*(2*j+1)//self.row_num,self.center[1]*(2*i+1)//self.row_num),self.data[i][j],self.size[0]*0.8//self.row_num,self.size[1]*0.8//self.row_num,window)
    
    #data:记录棋盘数据的二维数组
    def update(self,data):
        self.data=data 
       
        