import dns.resolver, re, threading, time
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from SuperClass import SuperClass

class SubDomainFinder(SuperClass):
    def __init__(self):
        super().__init__()
        self.subdomains = set()
        self.zoneTransfer = True
        self.crt = True
        self.archive = True
        self.hackertargetReverseS = True
        self.bruteForce = False
        self.wordlist = "/home/user/Subdomain.txt"
        self.resolver = dns.resolver.Resolver()
        self.resolver.nameservers = ['8.8.8.8', '8.8.4.4']
        self.total_subdomains = 0
        self.checked_subdomains = 0
        self.available = []

    def addSubdomains(self, subdomains):
        subdomains = [self.rawHost(url) for url in subdomains]
        self.subdomains.update(subdomains)

    def getSubdomains(self):
        return self.subdomains

    def setWordlist(self, wordlist): #todo: do we need every setter/getter here?
        self.wordlist = wordlist

    def getWordlist(self):
        return self.wordlist

    def subDomainProcess(self, url):
        if self.getZoneTransfer():
            self.DNSZoneTransfer(url)
        if self.getCrt():
            self.CTLogs(url)
        if self.getArchive():
            self.WaybackMachine(url)
        if self.getHackertargetReverseS():
            self.hackertargetReverseSubdomain(url)
        if self.getHackertargetHost():
            self.hackertargetHost(url)
        if self.getBruteForce():
            self.BruteForce(url)

    def getList(self, url): #todo: do we keep everything in memory?
        with open(self.wordlist, 'r') as f:
            subs = [f"{subdomain.strip()}.{self.rawHost(url)}" for subdomain in f.readlines()]
            self.total_subdomains = len(subs)
            return subs

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
        num = len(self.getSubdomains())
        self.addSubdomains(subdomains)
        print(f"Success! Found {len(self.getSubdomains()) - num} new subdomains\n")

    def CTLogs(self, url):
        print("Enumerating subdomains with CT logs from crt.sh...")
        domain = self.rawHost(url)
        url = f'https://crt.sh/?q=%.{domain}&output=json'
        response = self.makeRequest(url, retries=5, keep_session=False)
        if not response:
            print("Unable to connect to crt.sh\n")
            return
        if response.status_code == 200:
            ct_logs = response.json()
            subdomains = set()
            for log in ct_logs:
                subdomains.add(log['name_value'].split("\n")[0])
            num = len(self.getSubdomains())
            self.addSubdomains(subdomains)
            print(f"Success! Found {len(self.getSubdomains()) - num} new subdomains\n")
            return
        else:
            print(f"Unexpected status code: {response.status_code} ({url})")


    def WaybackMachine(self, url):
        print("Enumerating subdomains with Wayback Machine...")
        domain = self.rawHost(url)
        url = f"https://web.archive.org/cdx/search/cdx?url=*.{domain}/&output=json&collapse=urlkey&page=/"
        subdomains = set()
        response = self.makeRequest(url, retries=5, keep_session=False)
        if not response:
            print("Unable to connect to the Wayback Machine\n")
            return
        if response.status_code == 200:
            snapshots = response.json()
            for snapshot in snapshots:
                snapshot_url = snapshot[2]
                subdomain_match = re.search(r'^(https?:\/\/)?([\w\d\-]+\.)+[\w\d\-]+', snapshot_url)
                if subdomain_match:
                    subdomain = subdomain_match.group()
                    subdomains.add(subdomain)
            num = len(self.getSubdomains())
            self.addSubdomains(subdomains)
            print(f"Success! Found {len(self.getSubdomains()) - num} new subdomains\n")
            return
        else:
            print(f"Unexpected status code: {response.status_code} ({url})")

    def hackertargetReverseSubdomain(self, url):
        print("Enumerating subdomains with Hackertarget reverse IP lookup...")
        IP = self.getIP(url)
        if IP:
            api = f"https://api.hackertarget.com/reverseiplookup/?q={IP}"
            response = self.makeRequest(api, retries=5, keep_session=False)
            if not response:
                print("Unable to connect to Hackertarget")
            if response.status_code == 200:
                if 'API count exceeded' in response.text:
                    print("API count exceeded\n")
                    return
                subdomains = [subdomain for subdomain in response.text.split("\n") if self.rawHost(url) in subdomain]
                num = len(self.getSubdomains())
                self.addSubdomains(subdomains)
                print(f"Success! Found {len(self.getSubdomains()) - num} new subdomains\n")
                return
            else:
                print(f"Unexpected status code: {response.status_code} ({url})")

    def hackertargetHost(self, url):
        print("Enumerating subdomains with Hackertarget hostsearch API...")
        domain = self.rawHost(url)
        url = f"https://api.hackertarget.com/hostsearch/?q={domain}"
        response = self.makeRequest(url, retries=5, keep_session=False)
        if not response:
            print("Unable to connect to Hackertarget")
        if response.status_code == 200:
            if 'API count exceeded' in response.text:
                print("API count exceeded\n")
                return
            subdomains = [subdomain for subdomain in response.text.split("\n") if subdomain]
            subdomains = [subdomain.split(",")[0] for subdomain in subdomains]
            num = len(self.getSubdomains())
            self.addSubdomains(subdomains)
            print(f"Success! Found {len(self.getSubdomains()) - num} new subdomains\n")
            return
        else:
            print(f"Unexpected status code: {response.status_code} ({url})")

    def BruteForce(self, url):
        print("Preparing for bruteforce. It wouldn't take more than a minute...\n")
        subdomains = self.getList(url)
        self.resolver.nameservers += self.checkNameservers(self.getNameservers()) #todo: it doesn't speed anything up. we need another way
        threads = min(self.getSysThreads(), len(subdomains))
        print(f'Bruteforcing. It may take some time...')
        self.start_progress_printing()
        with ThreadPoolExecutor(max_workers=threads) as executor:
            executor.map(self.checkSubdomain, subdomains)

        num = len(self.getSubdomains())
        self.addSubdomains(self.available)
        print(f"Finished! Found {len(self.getSubdomains()) - num} new subdomains\n")

    def checkSubdomain(self, subdomain):
        subdomain = subdomain.strip()
        self.checked_subdomains += 1
        try:
            self.resolver.resolve(subdomain, 'A')
            self.available.append(subdomain)
            return True
        except:
            return False

    def print_progress(self):
        print(f"Checked {self.checked_subdomains}/{self.total_subdomains} subdomains...")

    def start_progress_printing(self):
        def print_progress_every_minute():
            while self.checked_subdomains < self.total_subdomains:
                self.print_progress()
                time.sleep(10)

        progress_thread = threading.Thread(target=print_progress_every_minute)
        progress_thread.start()

    def getNameservers(self):
        response = self.makeRequest("https://public-dns.info/nameservers.txt", retries=5)
        if response.status_code == 200:
            nameservers = response.text.split("\n")
        return nameservers

    def checkNameserver(self, nameserver):
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [nameserver]
        try:
            resolver.resolve('google.com', 'A')
            return True
        except:
            return False

    def checkNameservers(self, nameservers):
        valids = []
        threads = self.getSysThreads()
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(self.checkNameserver, ns): ns for ns in nameservers}
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

    def setHackertargetReverseS(self, value):
        self.HackertargetReverseS = value

    def setHackertargetHost(self, value):
        self.HackertargetHost = value

    def getArchive(self):
        return self.archive

    def getHackertargetReverseS(self):
        return self.HackertargetReverseS

    def getHackertargetHost(self):
        return self.HackertargetHost

    def setBruteForce(self, value):
        self.bruteForce = value

    def getBruteForce(self):
        return self.bruteForce
