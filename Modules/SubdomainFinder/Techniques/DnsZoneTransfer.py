from Engine.Engine import Engine
import dns.resolver


class DnsZoneTransfer(Engine):

    def process(self, url):
        print("Enumerating subdomains with DNS zone transfer...")
        domain = self.raw_host(url)
        resolver = dns.resolver.Resolver()
        resolver.proxies = self.get_proxy()
        subdomains = set()
        try:
            ns_answer = resolver.resolve(domain, 'NS')
            for server in ns_answer:
                ip_answer = resolver.resolve(server.target, 'A')
                for ip in ip_answer:
                    try:
                        zone = dns.zone.from_xfr(dns.query.xfr(str(ip), domain))
                        for host in zone:
                            subdomain = str(host)
                            subdomains.add(subdomain)
                            self.logger.log_info(f"Discovered subdomain: {subdomain}")
                    except Exception as e:
                        self.logger.log_error(f"Error during zone transfer: {e}")
        except dns.resolver.NXDOMAIN:
            self.logger.log_error("Domain not found.")
        except dns.exception.Timeout:
            self.logger.log_error("DNS query timed out.")
        except Exception as e:
            self.logger.log_error(f"An error occurred: {e}")
        return subdomains
