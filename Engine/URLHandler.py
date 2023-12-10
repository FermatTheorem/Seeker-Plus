import socket
import threading
from urllib.parse import urlparse, urlunparse
from typing import List, Tuple, Optional


class URLHandler:
    target: Optional[str] = None
    num_threads: int = 5

    def raw_host(self, url: str | None = None) -> str:
        url = self.target if url is None else url
        parsed_url = urlparse(self.get_url(url))
        hostname = parsed_url.hostname if parsed_url.hostname[:4] != "www." else parsed_url.hostname[4:]
        return hostname

    def set_target(self, url: str) -> None:
        self.target = url

    def get_target(self) -> Optional[str]:
        return self.target

    def get_ip(self, url: str | None = None) -> Optional[str]:
        url = self.target if url is None else url
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

    def raw_path(self, url: str | None = None) -> str:
        url = self.target if url is None else url
        parsed_url = urlparse(url)
        return parsed_url.netloc + parsed_url.path

    def get_url(self, url: str | None = None) -> str:
        url = self.target if url is None else url
        parsed_url = urlparse(url)

        if not parsed_url.scheme:
            url = 'https://' + url

        if parsed_url.port:
            url_parts = list(parsed_url)
            url_parts[0] = parsed_url.scheme or 'http'
            url_parts[1] = parsed_url.hostname + (f':{parsed_url.port}' if parsed_url.port != 80 else '')
            url = urlunparse(url_parts)

        return url
