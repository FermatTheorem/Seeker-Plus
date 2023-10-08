from Engine.Engine import Engine
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from time import time
import threading
import dns.resolver


class Bruteforce(Engine):

    def __init__(self):
        super().__init__()
        self._resolver = dns.resolver.Resolver()
        self._resolver.nameservers = ['8.8.8.8', '8.8.4.4']
        self._available = []
        self._total_subdomains = 0
        self._checked_subdomains = 0
        self._wordlist = "Misc/wordlist.txt"

    def process(self, url):
        print("Preparing for bruteforce. It wouldn't take more than a minute...\n")
        subdomains = self._get_list(url)
        self._resolver.nameservers += self._check_nameservers(
            self._get_nameservers())  # todo: it doesn't speed anything up. we need another way
        threads = min(self.get_sys_threads(), len(subdomains))
        print(f'Bruteforcing. It may take some time...')
        self._start_progress_printing()
        with ThreadPoolExecutor(max_workers=threads) as executor:
            executor.map(self._check_subdomain, subdomains)
        return self._available

    def _get_list(self, url): #todo: do we keep everything in memory?
        with open(self._wordlist, 'r') as f:
            subs = [f"{subdomain.strip()}.{self.raw_host(url)}" for subdomain in f.readlines()]
            self._total_subdomains = len(subs)
            return subs

    def _check_subdomain(self, subdomain):
        subdomain = subdomain.strip()
        self._checked_subdomains += 1
        try:
            self._resolver.resolve(subdomain, 'A')
            self._available.append(subdomain)
            return True
        except:
            return False

    def _print_progress(self):
        print(f"Checked {self._checked_subdomains}/{self._total_subdomains} subdomains...")

    def _start_progress_printing(self):
        def print_progress_every_minute():
            while self._checked_subdomains < self._total_subdomains:
                self._print_progress()
                time.sleep(10)

        progress_thread = threading.Thread(target=print_progress_every_minute)
        progress_thread.start()

    def _get_nameservers(self):
        response = self.make_request("https://public-dns.info/nameservers.txt", retries=5)
        if response.status_code == 200:
            nameservers = response.text.split("\n")
            return nameservers
        return ["8.8.8.8"]

    def _check_nameserver(self, nameserver):
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [nameserver]
        try:
            resolver.resolve('google.com', 'A')
            return True
        except:
            return False

    def _check_nameservers(self, nameservers):
        valids = []
        threads = self.get_sys_threads()
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(self._check_nameserver, ns): ns for ns in nameservers}
            done, not_done = wait(futures, timeout=60, return_when=FIRST_COMPLETED)
            for future in done:
                try:
                    if future.result():
                        valids.append(futures[future])
                except:
                    pass

            for future in not_done:
                future.cancel()

        return valids

    def _set_wordlist(self, wordlist):
        self._wordlist = wordlist

    def _get_wordlist(self):
        return self._wordlist