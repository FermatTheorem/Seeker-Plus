from Engine.Engine import Engine
import dns.resolver


class DnsZoneTransfer(Engine):

    def process(self, url):
        self.log_info("Enumerating subdomains with DNS zone transfer...")
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
                            self.log_info(f"Discovered subdomain: {subdomain}")
                    except Exception:
                        self.log_exception(f"Error during zone transfer")
        except dns.resolver.NXDOMAIN:
            self.log_exception("Domain not found")
        except dns.exception.Timeout:
            self.log_exception("DNS query timed out")
        except Exception:
            self.log_exception(f"An error occurred")
        return subdomains
