class BasePage:
    def __init__(self):
        self.visible = True
        self.pages: list[BasePage] = []
    
    def close(self):
        self.parent.remove_page(self)
    def run(self):
        raise NotImplementedError
    def add_page(self, page):
        raise NotImplementedError
    def get_page(self, page):
        raise NotImplementedError
    def remove_page(self, page):
        raise NotImplementedError