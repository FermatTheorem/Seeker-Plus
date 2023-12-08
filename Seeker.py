from Engine.Loader import load_modules
from Crawler.Crawler import Crawler
from Engine.Engine import Engine
from config import CONFIG


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
        module.set_target(CONFIG["Target"])
        module.set_response_timeout(CONFIG["HttpClient"]["response_timeout"])
        # module.use_tor_proxy()
        module.use_random_user_agent = CONFIG["HttpClient"]["use_random_user_agent"]
        module.set_output_dir(CONFIG["General"]["output_directory"])
        module.set_max_parallel_requests(CONFIG["HttpClient"]["max_parallel_requests"])
        # if not module.check_tor_proxy():
        #     raise "Tor isn't set up correctly"

if not CONFIG or not CONFIG["General"]:
    print("Incorrect config")
    exit(1)
scanner = Seeker()
scanner.process()