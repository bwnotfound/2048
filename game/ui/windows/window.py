from abc import ABC,abstractmethod
import pygame

class Window(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def show(self,window:pygame.Surface):
        pass
    
    def onclick(self,mouse_pos:(int,int)):
        pass
    
    def update(self):
        pass
    
