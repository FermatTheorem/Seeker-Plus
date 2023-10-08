import socket
import threading
from urllib.parse import urlparse, urlunparse
from typing import List, Tuple, Optional


class URLHandler:
    def __init__(self) -> None:
        self.target: Optional[str] = None
        self.num_threads: int = 5

    def raw_host(self, url: str) -> str:
        parsed_url = urlparse(self.get_url(url))
        hostname = parsed_url.hostname if parsed_url.hostname[:4] != "www." else parsed_url.hostname[4:]
        return hostname

    def set_target(self, url: str) -> None:
        self.target = url

    def get_target(self) -> Optional[str]:
        return self.target

    def get_ip(self, url: str) -> Optional[str]:
        host = self.raw_host(url)
        try:
            ip = socket.gethostbyname(host)
            return ip
        except socket.error:
            return None

    def validate_url(self, url: str) -> bool:
        try:
            socket.gethostbyname(self.raw_host(url))
            return True
        except socket.error:
            return False

    def validate_urls(self, url_list: List[str]) -> Tuple[List[str], List[str]]:
        valid_urls: List[str] = []
        invalid_urls: List[str] = []
        threads: List[threading.Thread] = []

        def validate_url_thread(url: str) -> None:
            if self.validate_url(url):
                valid_urls.append(url)
            else:
                invalid_urls.append(url)

        for url in url_list:
            thread = threading.Thread(target=validate_url_thread, args=(url,))
            threads.append(thread)
            thread.start()

            while len(threads) >= self.num_threads:
                threads = [t for t in threads if t.is_alive()]
                if len(threads) >= self.num_threads:
                    threads[0].join()

        for thread in threads:
            thread.join()

        return valid_urls, invalid_urls

    def raw_path(self, url: str) -> str:
        parsed_url = urlparse(url)
        return parsed_url.netloc + parsed_url.path

    def get_url(self, url: str) -> str:
        parsed_url = urlparse(url)

        if not parsed_url.scheme:
            url = 'https://' + url

        if parsed_url.port:
            url_parts = list(parsed_url)
            url_parts[0] = parsed_url.scheme or 'http'
            url_parts[1] = parsed_url.hostname + (f':{parsed_url.port}' if parsed_url.port != 80 else '')
            url = urlunparse(url_parts)

        return url

# url_handler = URLHandler()
#
# # Set and get the target URL
# url_handler.set_target("http://www.example.com?parameter=value")
# print(url_handler.get_target())  # Output: http://www.example.com?parameter=value
#
# # Get the raw hostname
# print(url_handler.raw_host("http://www.example.com?parameter=value"))  # Output: example.com
#
# # Get the IP address of a URL
# print(url_handler.get_ip("http://www.example.com"))  # Output: IP address or None
#
# # Validate a URL
# print(url_handler.validate_url("http://www.example.com"))  # Output: True or False
#
# # Validate a list of URLs
# url_list = ["http://www.example.com", "http://www.iaxcxznvalid-url.com"]
# valid_urls, invalid_urls = url_handler.validate_urls(url_list)
# print("Valid URLs:", valid_urls)
# print("Invalid URLs:", invalid_urls)
#parsed_url.scheme
# # Get the raw path
# print(url_handler.raw_path("https://www.example.com/path/to/script?parameter=value"))  # Output: example.com/path/to/script
