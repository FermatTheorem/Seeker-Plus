from Engine.Engine import Engine


class Hackertarget(Engine):

    def process(self, url):
        self.subdomains = set()
        self.reverseiplookup(url)
        self.hostsearch(url)
        return self.subdomains

    def reverseiplookup(self, url):
        print("Enumerating subdomains with Hackertarget reverse IP lookup...")
        IP = self.get_ip(url)
        if IP:
            api = f"https://api.hackertarget.com/reverseiplookup/?q={IP}"
            response = self.make_request(api, retries=5, keep_session=False)
            if not response:
                self.logger.log_error("Unable to connect to Hackertarget")
            if response.status_code == 200:
                if 'API count exceeded' in response.text:
                    self.logger.log_info("API count exceeded\n")
                    return
                subdomains = set([subdomain for subdomain in response.text.split("\n") if self.raw_host(url) in subdomain])
                self.subdomains.update(subdomains)
                return
            else:
                self.logger.log_info(f"Unexpected status code: {response.status_code} ({url})")

    def hostsearch(self, url):
        print("Enumerating subdomains with Hackertarget hostsearch API...")
        domain = self.raw_host(url)
        url = f"https://api.hackertarget.com/hostsearch/?q={domain}"
        response = self.make_request(url, retries=5, keep_session=False)
        if not response:
            self.logger.log_error("Unable to connect to Hackertarget")
        if response.status_code == 200:
            if 'API count exceeded' in response.text:
                self.logger.log_info("API count exceeded\n")
                return
            subdomains = [subdomain for subdomain in response.text.split("\n") if subdomain]
            subdomains = set([subdomain.split(",")[0] for subdomain in subdomains])
            self.subdomains.update(subdomains)
            return
        else:
            self.logger.log_info(f"Unexpected status code: {response.status_code} ({url})")