from Engine.Engine import Engine
import re


class WebArchive(Engine):

    def process(self, url):
        self.log_info("Enumerating subdomains with Wayback Machine...")
        domain = self.raw_host(url)
        url = f"https://web.archive.org/cdx/search/cdx?url=*.{domain}/&output=json&collapse=urlkey&page=/"
        subdomains = set()
        response = self.make_request(url, retries=5, keep_session=False)
        if not response:
            self.log_error("Unable to connect to the Wayback Machine\n")
            return
        if response.status_code == 200:
            snapshots = response.json()
            for snapshot in snapshots:
                snapshot_url = snapshot[2]
                subdomain_match = re.search(r'^(https?:\/\/)?([\w\d\-]+\.)+[\w\d\-]+', snapshot_url)
                if subdomain_match:
                    subdomain = subdomain_match.group()
                    subdomains.add(subdomain)
            return subdomains
        else:
            self.log_error(f"Unexpected status code: {response.status_code} ({url})")
