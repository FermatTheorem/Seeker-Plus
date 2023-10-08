#!/usr/bin/env python3
import argparse
from Engine.Loader import load_modules
from Crawler.Crawler import Crawler
from Engine.Engine import Engine


def print_banner():
    banner = """

 _____         _                _   
|   __|___ ___| |_ ___ ___    _| |_ 
|__   | -_| -_| '_| -_|  _|  |_   _|
|_____|___|___|_,_|___|_|      |_|  

    Seeker Plus - Yet Another Web Scanning Tool
    Made by @FermatTheorem
    """
    print(banner)

class Seeker(Engine):

    def __init__(self) -> None:
        self._crawler: Crawler = Crawler()
        self._modules: list[object] = load_modules("Modules")

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

    def _configure(self, module: object) -> None:
        module.set_target("https://www.kantiana.ru/")
        module.set_response_timeout(60)
        module.use_tor_proxy()
        module.use_random_user_agent = True
        module.set_output_dir("Output")
        module.set_max_parallel_requests(50)
        if not module.check_tor_proxy():
            raise "Tor isn't set up correctly"

scanner = Seeker()
scanner.process()