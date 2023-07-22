from Scanner import Scanner
import dns.resolver
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor

class SubDomainFinder(Scanner):
    def __init__(self):
        super().__init__()
        self.zoneTransfer = True
        self.crt = True
        self.archive = True
        self.bruteForce = True
        self.bruteThreads = 100 #todo: speed up to the sky
        self.wordlist = "/home/user/Subdomain.txt"
        self.resolver = dns.resolver.Resolver()
        self.resolver.nameservers = ['8.8.8.8', '8.8.4.4'] #todo: add a nameservers collector
        self.total_subdomains = 0
        self.checked_subdomains = 0
        self.available = []

    def setWordlist(self, wordlist): #todo: do we need every setter/getter here?
        self.wordlist = wordlist

    def getWordlist(self):
        return self.wordlist

    def setZoneTransfer(self, value):
        self.zoneTransfer = value

    def getZoneTransfer(self):
        return self.zoneTransfer

    def setCrt(self, value):
        self.crt = value

    def getCrt(self):
        return self.crt

    def setArchive(self, value):
        self.archive = value

    def getArchive(self):
        return self.archive

    def setBruteForce(self, value):
        self.bruteForce = value

    def getBruteForce(self):
        return self.bruteForce

    def setBruteThreads(self, num):
        self.bruteThreads = num

    def getBruteThreads(self):
        return self.bruteThreads

    def subDomainProcess(self, url):
        if self.getZoneTransfer():
            self.DNSZoneTransfer(url)
        if self.getCrt():
            self.CTLogs(url)
        if self.getArchive():
            self.WaybackMachine(url)
        if self.getBruteForce():
            self.BruteForce(url)

    def getList(self, url): #todo: do we keep everything in memory?
        with open(self.wordlist, 'r') as f:
            subs = [f"{subdomain.strip()}.{self.rawHost(url)}" for subdomain in f.readlines()]
            self.total_subdomains = len(subs)
            return subs

    def checkSubdomain(self, subdomain):
        subdomain = subdomain.strip()
        self.checked_subdomains += 1
        try:
            self.resolver.resolve(subdomain, 'A')
            self.available.append(subdomain)
            return True
        except:
            return False

    def BruteForce(self, url):
        subdomains = self.getList(url)
        threads = min(self.getBruteThreads(), len(subdomains))
        print(f'Bruteforcing subdomains. It may take some time...')
        self.start_progress_printing()
        with ThreadPoolExecutor(max_workers=threads) as executor:
            executor.map(self.checkSubdomain, subdomains)
        print(self.available)

    def print_progress(self):
        print(f"Checked {self.checked_subdomains}/{self.total_subdomains} subdomains...")

    def start_progress_printing(self):
        def print_progress_every_minute():
            while self.checked_subdomains < self.total_subdomains:
                self.print_progress()
                time.sleep(10)

        progress_thread = threading.Thread(target=print_progress_every_minute)
        progress_thread.start()

    def DNSZoneTransfer(self, url): #todo: does this even work?
        print("Enumerating subdomains with DNS zone transfer...")
        domain = self.rawHost(url)
        resolver = dns.resolver.Resolver()
        resolver.proxies = self.getProxy()
        ns_answer = resolver.resolve(domain, 'NS')
        subdomains = set()
        for server in ns_answer:
            ip_answer = resolver.resolve(server.target, 'A')
            for ip in ip_answer:
                try:
                    zone = dns.zone.from_xfr(dns.query.xfr(str(ip), domain))
                    for host in zone:
                        subdomains.add(str(host))
                except Exception as e:
                    pass
        print("Success!")
        self.addSubdomains(subdomains)

    def CTLogs(self, url):
        print("Enumerating subdomains with CT logs in crt.sh...")
        domain = self.rawHost(url)
        url = f'https://crt.sh/?q=%.{domain}&output=json'
        response = self.makeRequest(url, retries=5)
        if not response:
            return
        if response.status_code == 200:
            ct_logs = response.json()
            subdomains = set()
            for log in ct_logs:
                subdomains.add(log['name_value'].split("\n")[0])
            self.addSubdomains(subdomains)
            print("Success!")
            return
        else:
            print(f"Unexpected status code: {response.status_code} ({url})")

    def WaybackMachine(self, url):
        print("Enumerating subdomains with Wayback Machine...")
        domain = self.rawHost(url)
        url = f"https://web.archive.org/cdx/search/cdx?url=*.{domain}/&output=json&collapse=urlkey&page=/"
        subdomains = set()
        response = self.makeRequest(url, retries=5)
        if not response:
            return
        if response.status_code == 200:
            snapshots = response.json()
            for snapshot in snapshots:
                snapshot_url = snapshot[2]
                subdomain_match = re.search(r'^(https?:\/\/)?([\w\d\-]+\.)+[\w\d\-]+', snapshot_url)
                if subdomain_match:
                    subdomain = subdomain_match.group()
                    subdomains.add(subdomain)
            print("Success!")
            self.addSubdomains(subdomains)
            return
        else:
            print(f"Unexpected status code: {response.status_code} ({url})")
        print("Unable to connect to the Wayback Machine")