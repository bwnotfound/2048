class PageManager:
    def __init__(self):
        self.page_dict = {}

    def get_page_list(self):
        return list(self.page_dict.values())

    def close(self):
        pass

    def del_page(self, name):
        if not isinstance(name, str):
            for k, v in self.page_dict.items():
                if name is v:
                    self.page_dict.pop(k)
                    return
        if name in self.page_dict:
            del self.page_dict[name]

    def add_page(self, *args):
        if len(args) == 1:
            page = args[0]
            name = page.__class__.__name__
        else:
            page, name = args
        self.page_dict[name] = page
