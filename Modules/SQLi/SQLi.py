from Engine.Engine import Engine

class SQLi(Engine):
    def __init__(self):
        super().__init__()
        self.needs_crawl: bool = True

    # def process(self, page):
        # print(page)
        # print(page.url)
        # print(page.status_code)
        # print(page.params)
        # todo
    def process(self):
        pass