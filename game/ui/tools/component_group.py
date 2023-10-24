import pygame


class ComponentGroup:
    def __init__(self, part_list: list):
        self.show_list = []
        self.onclick_list = []
        for part in part_list:
            if hasattr(part, 'show'):
                self.show_list.append(part)
            if hasattr(part, 'onclick'):
                self.onclick_list.append(part)

    def show(self, window: pygame.Surface):
        for part in self.show_list:
            part.show(window)

    # update相比于show,在于会更新背景，所以我为什么没有删掉show。。
    def update(
        self, window: pygame.Surface, background_img=None, background_color=None
    ):
        r"""
            建议background_img和background_color选其一调用,默认background_img覆盖background_color
        """
        if background_color is not None:
            window.fill(background_color)
        if background_img is not None:
            window.blit(background_img, (0, 0))
        for part in self.show_list:
            part.show(window)

    def onclick(self, mouse_pos):
        ret_list = []
        for part in self.onclick_list:
            if part.onclick(mouse_pos):
                print(part.get_text())
                ret_list.append(part)
        return ret_list

    def add_compo(self, compo):
        if hasattr(compo, 'show'):
            self.show_list.append(compo)
        if hasattr(compo, 'onclick'):
            self.onclick_list.append(compo)

    def del_compo(self, compo):
        self.show_list = [i for i in self.show_list if i is not compo]
        self.onclick_list = [i for i in self.onclick_list if i is not compo]
