import requests
import os
from time import sleep
import fake_useragent
from concurrent.futures import ThreadPoolExecutor, as_completed, CancelledError
import logging
from requests.exceptions import RequestException
import threading
import subprocess

class Scanner:

    def __init__(self):
        self.proxies = None
        self.neighbors = set()
        self.outputDir = 'output'
        self.headers = {}
        self.target = None
        self.useRandomUA = False
        self.session = requests.Session()
        self.timeout = 5
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.threadsCount = 1

    def setTarget(self, url):
        url = url if url.startswith("http") else "https://" + url
        self.target = url

    def getTarget(self):
        return self.target

    def addNeighbors(self, neighbors):
        self.neighbors.update(neighbors)

    def getNeighbors(self):
        return self.neighbors

    def setSysThreads(self, num):
        self.sysThreads = num

    def getSysThreads(self):
        return self.sysThreads

    def checkConnection(self, url):
        print("Checking connection to the target...")
        try:
            response = self.makeRequest(url, retries=3)
            if response:
                print("Connected successfully")
                return True
        except Exception as e:
            print("Error connection: ", e)
            return False

    def setProxy(self, proxy):
        self.proxies = {'http': proxy, 'https': proxy}

    def getProxy(self):
        return self.proxies

    def checkTor(self):
        print("Checking tor configuration...")
        try:
            response = self.makeRequest('https://check.torproject.org/', retries=5)
            if 'Congratulations. This browser is configured to use Tor.' in response.text:
                print("Tor is properly being used!\n")
                return True
        except:
            pass
        print("Tor isn't set up properly. Check your proxy")
        exit(1)

    def setTor(self, port=9050):
        self.setProxy('socks5://localhost:' + str(port))

    def setUserAgent(self, user_agent):
        self.setHeaders['User-Agent'] = user_agent

    def getUserAgent(self):
        return self.headers['User-Agent']

    def setOutputDir(self, dir='output'):
        if not os.path.isdir(dir):
            try:
                os.makedirs(dir)
            except Exception as e:
                raise f"Error creating a direcotory {dir}: {e}"
        self.outputDir = dir

    def getOutputDir(self):
        return self.outputDir

    def setHeaders(self, headers):
        assert type(headers) == dict, 'Headers must be a dictionary'
        self.headers = headers

    def getHeaders(self):
        return self.headers

    def newSession(self):
        self.session = requests.Session()

    def setCookies(self, cookies):
        self.session.cookies.update(cookies)

    def getCookies(self):
        return self.session.cookies.get_dict()

    def setThreads(self, num):
        self.threadsCount = num

    def getThreads(self):
        return self.threadsCount

    def makeRequest(self, url, method='GET', data={}, retries=1, keep_session=True):
        if not keep_session:
            self.newSession()
        headers = self.getHeaders()
        url = url if url.startswith('http') else 'https://' + url
        for i in range(retries):
            if self.useRandomUA:
                headers["User-Agent"] = fake_useragent.UserAgent().random
            try:
                if method == 'GET':
                    response = self.session.get(url, headers=headers, proxies=self.getProxy(), timeout=self.getTimeout())
                elif method == 'POST':
                    response = self.session.post(url, data=data, headers=headers, proxies=self.getProxy(), timeout=self.getTimeout())
                return response
            except RequestException as e:
                self.logger.error(f"Request failed for {url} with error {e}")
                sleep(2)
        return None

    def makeConcurrentRequests(self, targets, method='GET', data={}, retries=1, max_workers=None, keep_session=True):
        if not max_workers:
            max_workers = min(self.getThreads(), len(targets))
        results = {}
        lock = threading.Lock()
        for i in range(0, len(targets), max_workers):
            urls = targets[i:max_workers + i]
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(self.makeRequest, url, method, data, retries, keep_session): url for url in urls}

            for future in as_completed(futures):
                url = futures[future]
                try:
                    result = future.result()
                    with lock:  # ensure thread safety when updating the results dictionary
                        results[url] = result
                except CancelledError as e:
                    self.logger.error(f"Error processing {url}: {e}")
                    with lock:
                        results[url] = None

        return results

    def rawHost(self, url):
        url = url.split("://")[1] if "://" in url else url
        return url.replace("www.", "").rstrip("/")

    def validateUrl(self, url): #we need another way. That one isn't suitable with proxy and brings false positives
        command = ['ping', '-c', '1', self.rawHost(url)]
        return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

    def validateUrls(self, urls):
        print("Validating urls...")
        max_workers = min(self.getSysThreads(), len(urls))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.validateUrl, url) for url in urls]
        return [url for future, url in zip(futures, urls) if future.result()]

    def setRandomUA(self):
        self.useRandomUA = True

    def setTimeout(self, timeout):
        assert isinstance(timeout, (int, float)), 'Timeout must be a number'
        self.timeout = timeout

    def getTimeout(self):
        return self.timeout

    def setLoggingLevel(self, level): #todo: add logging support for everything
        assert level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], 'Invalid logging level'
        self.logger.setLevel(level)

    def getLoggingLevel(self):
        return self.logger.level
