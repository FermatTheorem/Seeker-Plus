from typing import Any

from Engine.Loader import load_modules
from Crawler.Crawler import Crawler
from Engine.Engine import Engine
from config import get_from_config


class Seeker(Engine):

    def __init__(self) -> None:
        self._crawler: Crawler = Crawler()
        self._modules: list[Any] = load_modules()

    def process(self) -> None:
        for module in self._modules:
            module = module()
            self._configure(module)
            if hasattr(module, "needs_crawl") and module.needs_crawl:
                self._crawl()
                for page in self._crawler.pages:
                    module.process(self._crawler.pages[page])
            else:
                module.process()

    def _crawl(self) -> None:
        if self._crawler.pages == {}:
            self._configure(self._crawler)
            self._crawler.process()

    def _configure(self, module: Any) -> None:
        module.logger.module_name = module.__class__.__name__
        if target := get_from_config(["Target"], str):
            module.set_target(target)
        else:
            raise RuntimeError("Unable to parse a target from a config")

        # General config section
        if output_directory := get_from_config(["General", "output_directory"], str):
            module.set_output_dir(output_directory)

        # HttpClient
        if use_random_user_agent := get_from_config(["HttpClient", "use_random_user_agent"], bool):
            module.use_random_user_agent = use_random_user_agent
        if response_timeout := get_from_config(["HttpClient", "response_timeout"], int):
            module.set_response_timeout(response_timeout)
        if max_parallel_requests := get_from_config(["HttpClient", "max_parallel_requests"], int):
            module.set_max_parallel_requests(max_parallel_requests)
        if headers := get_from_config(["HttpClient", "headers"], dict):
            module.set_headers(headers)

        proxy = {}
        if get_from_config(["HttpClient", "http_proxy", "enabled"], bool):
            http_address = get_from_config(["HttpClient", "http_proxy", "http_address"], str)
            http_port = get_from_config(["HttpClient", "http_proxy", "http_port"], int)
            proxy["http://"] = ":".join([http_address, http_port])
        if get_from_config(["HttpClient", "https_proxy", "enabled"], bool):
            https_address = get_from_config(["HttpClient", "https_proxy", "https_address"], str)
            https_port = get_from_config(["HttpClient", "https_proxy", "https_port"], int)
            proxy["https://"] = ":".join([https_address, https_port])
        if get_from_config(["HttpClient", "socks5_proxy", "enabled"], bool):
            socks5_address = get_from_config(["HttpClient", "socks5_proxy", "socks5_address"], str)
            socks5_port = get_from_config(["HttpClient", "socks5_proxy", "socks5_port"], int)
            proxy["socks5://"] = ":".join([socks5_address, socks5_port])
        if proxy != {}:
            self.set_proxy(proxy)


scanner = Seeker()
scanner.process()