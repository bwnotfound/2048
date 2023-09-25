import pygame


class Comp_Collection:
    def __init__(self, part_list: list):
        self.show_list=[]
        for part in part_list:
            if hasattr(part,'show'):   
                self.show_list.append(part)
        self.onclick_list=[]
        for part in part_list:
            if hasattr(part,'onclick'):   
                self.onclick_list.append(part)

    def show(self, window: pygame.Surface):
        for part in self.show_list:
            if hasattr(part, 'show'):
                part.show(window)

    def update(self, window: pygame.Surface, background_img=None, background_color=(0, 0, 0)):
        if background_img == None:
            window.fill(background_color)
        else:
            window.blit(background_img, (0, 0))
        for part in self.show_list:
            if hasattr(part, 'show'):
                part.show(window)
        pygame.display.flip()
    
    def onclick(self,mouse_pos):
        ret_list=[]
        for part in self.onclick_list:
            if part.onclick(mouse_pos):
                print(part.get_text())
                ret_list.append(part)
        return ret_list

    def add_compo(self, compo):
        if hasattr(compo,'show'):   
            self.show_list.append(compo)
        if hasattr(compo,'onclick'):   
            self.onclick_list.append(compo)

    def del_compo(self, compo):
        self.show_list = [i for i in self.show_list if i is not compo]
        self.onclick_list = [i for i in self.onclick_list if i is not compo]
