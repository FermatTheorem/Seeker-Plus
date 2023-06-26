import re
import requests
import os
from time import sleep
import fake_useragent


class Scanner:

    def __init__(self):
        self.proxies = None
        self.user_agent = None
        self.IPs = set()
        self.subdomains = set()
        self.outputDir = 'output'
        self.headers = {}
        self.target = None

    def setTarget(self, url):
        self.target = url

    def getTarget(self):
        return self.target

    def addIP(self, IP):
        self.IPs.update(IP)

    def getIPs(self):
        return self.IPs

    def checkConnection(self, url):
        print("Checking connection to the target...")
        try:
            response = self.makeRequest(url)
            if response.status_code == 200:
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
            response = self.makeRequest('https://check.torproject.org/')
            if 'Congratulations. This browser is configured to use Tor.' in response.text:
                print("Tor is properly being used!")
                return True
        except:
            pass
        print("Tor isn't set up properly. Check your proxy")

    def setTor(self, port=9050):
        self.setProxy('socks5://localhost:' + str(port))

    def setUserAgent(self, user_agent):
        self.user_agent = user_agent

    def getUserAgent(self):
        return self.user_agent

    def setOutputDir(self, dir='output'):
        assert os.path.isdir(dir), 'Invalid directory path'
        self.outputDir = dir

    def getOutputDir(self):
        return self.outputDir

    def addSubdomains(self, subdomains):
        self.subdomains.update(subdomains)
        self.removeDuplicates()

    def getSubdomains(self):
        return self.subdomains

    def setHeaders(self, headers):
        assert type(headers) == dict, 'Headers must be a dictionary'
        self.headers = headers

    def getHeaders(self):
        return self.headers

    def makeRequest(self, url):
        user_agent = self.getUserAgent()
        headers = {'User-Agent': user_agent} if user_agent else {}
        headers.update(self.getHeaders())
        for i in range(5):
            try:
                if not url.startswith('http'):
                    try:
                        response = requests.get('https://' + url, headers=headers, proxies=self.getProxy())
                    except:
                        response = requests.get('http://' + url, headers=headers, proxies=self.getProxy())
                else:
                    response = requests.get(url, headers=headers, proxies=self.getProxy())
                return response
            except Exception as e:
                exc = e
                print(f"Error connecting to {url}. Retrying... [{i + 1}/5]")
                sleep(5)
        print(f'Unable to connect to {url} after 5 retries')
        print(exc)
        return None

    def removeDuplicates(self):
        self.subdomains = {domain.replace("http://", "").replace("https://", "").replace("www.", "") for domain in
                           self.getSubdomains()}

    def validateUrl(self, url):
        responce = self.makeRequest(url)
        if not responce:
            return False
        return True

    def setRandomUA(self):
        self.setUserAgent(fake_useragent.UserAgent().random)