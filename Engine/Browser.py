from selenium import webdriver
from HttpClient import RequestHandler
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import CONFIG, BROWSER_OPTIONS, HEADLESS_BROWSER

_conf = CONFIG["Browser"]
class Browser(RequestHandler):
    def __init__(self, headless=HEADLESS_BROWSER, options=BROWSER_OPTIONS):
        self.headless = _conf["headless"]
        self.options = options or self._get_default_options()
        self.driver = self._create_driver()

    def _get_default_options(self):
        options = webdriver.FirefoxOptions()
        if self.headless:
            options.headless = True
        return options

    def _create_driver(self):
        if self.get_proxy():
            proxy = self.get_proxy_dict()
            self.options.set_preference("network.proxy.type", 1)
            self.options.set_preference(f"network.proxy.{proxy['type']}", proxy["address"])
            self.options.set_preference(f"network.proxy.{proxy['type']}_port", proxy["port"])
            if "https" in self.proxy and proxy["type"] != "socks":
                self.options.set_preference("network.proxy.ssl", proxy["address"])
                self.options.set_preference("network.proxy.ssl_port", 443)

        driver = webdriver.Firefox(self.options)
        driver.set_page_load_timeout(self.get_response_timeout())
        return driver

    def single_request(self, url):
        url = self.get_url(url)
        self.driver.get(url)

    def multiple_requests(self, urls):
        for url in urls:
            self.single_request(url)

    def wait_for_element(self, by, value, timeout=10):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            raise Exception(f"Error waiting for element: {e}")
            return None

    def quit(self):
        if self.driver:
            self.driver.quit()


# # Example usage:
# if __name__ == "__main__":
#
#     # Create a Firefox browser instance with custom options
#     firefox_browser = Browser(
#         headless=False,
#     )
#
#     # Perform requests or other actions as needed
#     firefox_browser.single_request("google.com")
#     # Quit the browsers
#     firefox_browser.quit()
