from Scanner import Scanner
import dns.resolver
import re


class SubDomainFinder(Scanner):
    def DNSZoneTransfer(self, url):
        print("Enumerating with DNS zone transfer...")
        domain = url.split('//')[-1].split('/')[0]
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
        print("Enumerating with CT logs in crt.sh...")
        domain = url.split('//')[-1].split('/')[0]
        url = f'https://crt.sh/?q=%.{domain}&output=json'
        response = self.makeRequest(url)
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
        print("Enumerating with Wayback Machine...")
        domain = url.split('//')[-1].split('/')[0]
        url = f"https://web.archive.org/cdx/search/cdx?url=*.{domain}/&output=json&collapse=urlkey&page=/"
        subdomains = set()
        response = self.makeRequest(url)
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
