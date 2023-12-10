class BasePage:
    def __init__(self):
        self.visible = True
        self.pages: list[BasePage] = []

    def close(self):
        self.parent.remove_page(self)

    def run(self):
        raise NotImplementedError

    def add_page(self, page):
        if self.get_page(page) is not None:
            return
        self.pages.append(page)

    def get_page(self, page):
        for p in self.pages:
            if page is p:
                return page
        return None

    def remove_page(self, page):
        page = self.get_page(page)
        if page is not None:
            self.pages.remove(page)
