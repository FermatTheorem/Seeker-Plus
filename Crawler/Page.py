class Page:
    def __init__(self, url, params={}, post_data=None, response=None):
        self.url = url
        self.params = params
        self.post_data = post_data
        self.response = response

    @property
    def status_code(self):
        if self.response:
            return self.response.status_code
        return None

    @property
    def content(self):
        if self.response:
            return self.response.text
        return None

    def add_params(self, params: dict[str, str]) -> None:
        for key in params.keys():
            if key in self.params.keys():
                self.params[key].append(params[key])
            else:
                self.params[key] = params[key]
