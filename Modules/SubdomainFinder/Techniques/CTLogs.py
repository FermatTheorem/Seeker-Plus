from Engine.Engine import Engine

class CTLogs(Engine):

    def process(self, url):
        self.log_info("Enumerating subdomains with CT logs from crt.sh...")
        domain = self.raw_host(url)
        url = f'https://crt.sh/?q=%.{domain}&output=json'
        response = self.make_request(url, retries=5, keep_session=False)
        if not response:
            self.log_error("Unable to connect to crt.sh\n")
            return
        if response.status_code == 200:
            ct_logs = response.json()
            subdomains = set()
            for log in ct_logs:
                subdomains.add(log['name_value'].split("\n")[0])
            return subdomains
            self.log_info(f"Success! Found {len(self.get_subdomains()) - num} new subdomains\n")
            return
        else:
            self.log_error(f"Unexpected status code: {response.status_code} ({url})")
