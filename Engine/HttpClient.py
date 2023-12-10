import asyncio
import httpx
from fake_useragent import UserAgent
from .Logger import Logger
from .URLHandler import URLHandler
from typing import List, Optional, Union, Dict, Iterable


class RequestHandler(URLHandler, Logger):

    session: Optional[httpx.Client] = None
    headers: Dict[str, str] = {}
    response_timeout: int = 10
    max_parallel_requests: int = 5
    proxy: Optional[Dict[str, str]] = None
    use_random_user_agent: bool = True
    logger: Logger = Logger()

    def set_user_agent(self, user_agent: str) -> None:
        self.headers['User-Agent'] = user_agent

    def get_user_agent(self) -> str:
        return self.headers['User-Agent']

    def set_headers(self, headers: Dict[str, str]) -> None:
        self.headers = headers

    def get_headers(self) -> Dict[str, str]:
        return self.headers

    def set_response_timeout(self, timeout: float) -> None:
        self.response_timeout = timeout

    def get_response_timeout(self) -> float:
        return self.response_timeout

    def set_max_parallel_requests(self, max_parallel_requests: int) -> None:
        self.max_parallel_requests = max_parallel_requests

    def get_max_parallel_requests(self) -> int:
        return self.max_parallel_requests

    def set_proxy(self, proxies: Optional[Dict[str, str]]) -> None:
        self.proxy = proxies

    def get_proxy(self) -> Optional[Dict[str, str]]:
        return self.proxy

    def get_random_user_agent(self) -> str:
        ua = UserAgent()
        self.headers['User-Agent'] = ua.random
        return self.headers['User-Agent']

    def get_proxy_dict(self) -> Optional[dict[str, str | int]]:
        res = dict()
        for proxy in self.proxy:
            if "://" in self.proxy[proxy]:
                splitted = self.proxy[proxy].split("://", 1)
                res["type"], proxy = splitted[0], splitted[1]
            else:
                res["type"] = proxy
            if ":" in proxy:
                splitted = proxy.split(":", 1)
                res["address"] = splitted[0]
                res["port"] = splitted[1]

    def make_request(
            self,
            url: str,
            method: str = 'get',
            data: Optional[Union[None, str, Dict[str, str]]] = None,
            retries: int = 1,
            keep_session: bool = False
    ) -> Optional[httpx.Response]:
        url = self.get_url(url)
        for _ in range(retries + 1):
            if not keep_session or self.session is None:
                self.session = httpx.Client(proxies=self.proxy)
                if self.use_random_user_agent:
                    self.headers['User-Agent'] = self.get_random_user_agent()
            self.log_info(f"Making a {method.upper()} request to {url}")
            try:
                if method.lower() == 'get':
                    response = self.session.get(url, params=data, headers=self.headers, timeout=self.response_timeout)
                elif method.lower() == 'post':
                    response = self.session.post(url, data=data, headers=self.headers, timeout=self.response_timeout)
                else:
                    raise ValueError("Unsupported HTTP method: {}".format(method))
                self.log_info(f"Received a {response.status_code} status code")
                return response

            except Exception as e:
                if keep_session:
                    self.session = None
                self.log_error(f"Error making request to {url}: {str(e)}")
                continue

    def make_parallel_requests(
            self,
            urls: Iterable[str],
            method: str = 'get',
            data: Optional[Union[None, str, Dict[str, str]]] = None,
            retries: int = 3,
            keep_session: bool = False,
            limit: Optional[int] = None
    ) -> List[Optional[httpx.Response]]:
        if not limit:
            limit = self.max_parallel_requests

        async def make_request_async(url: str) -> Optional[httpx.Response]:
            return self.make_request(url, method, data, retries, keep_session)

        async def parallel_requests() -> List[Optional[httpx.Response]]:
            async with httpx.AsyncClient(proxies=self.proxy) as client:
                semaphore = asyncio.Semaphore(limit)

                async def limited_make_request(url: str) -> Optional[httpx.Response]:
                    async with semaphore:
                        return await make_request_async(url)

                tasks = [limited_make_request(url) for url in urls]
                return await asyncio.gather(*tasks)

        loop = asyncio.get_event_loop()
        responses = loop.run_until_complete(parallel_requests())
        return responses
