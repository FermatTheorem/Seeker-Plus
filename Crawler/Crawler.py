from html import unescape

from .Page import Page
from Engine.Engine import Engine


# todo: headless selenium (?) crawling

class Crawler(Engine):
    pages: dict[str, Page] = {}

    def process(self) -> None:
        self._wayback_params(self.get_target())
        self._get_responses()

    def _get_responses(self) -> None:
        queue = set()
        for page in self.pages:
            if not self.pages[page].response and self.pages[page].params:
                queue.add(page)
        responses = self.make_parallel_requests(queue, keep_session=False)
        for response in responses:
            if response.status_code != 404:
                self.pages[response.url].response = response

    def _wayback_params(self, url: str) -> None:
        domain = self.raw_host(url)
        wayback_url = f"web.archive.org/cdx/search/cdx?url={domain}/*&fl=original&collapse=urlkey&output=json&page=/"
        response = self.make_request(wayback_url, keep_session=False, retries=5)
        if response and response.status_code == 200:
            for endpoint in response.json()[1:]:
                url = self.get_url(endpoint[0])
                if self._is_static(url):
                    continue
                params = self._extract_params(url)
                url = url.split("?", 1)[0]
                page = Page(url)
                if params:
                    page.add_params(params)
                self.pages[url] = page

    def _get_raw_path(self, url: str) -> str:
        return self.raw_host(url).split("/")[0]

    def _extract_params(self, url: str) -> dict[str, str] | None:
        if "?" not in url or self._is_static(url):
            return
        result = dict()
        url = unescape(url)
        url = url.split("?", 1)[1]
        parameters = url.split("&")
        for parameter in parameters:
            if not parameter:
                continue
            key_value = parameter.split("=", 1)
            if len(key_value) == 1:
                key_value.append("")
            if key_value[0] not in result:
                result[key_value[0]] = []
            result[key_value[0]].append(key_value[1])
        return result

    def _is_static(self, url: str) -> bool:
        static_file_types = ['css', 'js', 'woff', 'woff2', 'png', 'jpg', 'jpeg', 'gif', 'svg', 'ico', 'pdf', 'txt', 'csv', 'xml', 'ttf', 'eot', 'doc', 'xls', 'docx', 'cur', 'htc', 'rtf', 'ppt']
        splitted = self.raw_path(url).split("/")
        if len(splitted) == 1:
            return False
        last = splitted[-1].lower()
        if "." in last:
            ext = last.split(".")[-1]
            return ext in static_file_types
        return False
