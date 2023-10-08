from Modules.SubdomainFinder.Techniques.Bruteforce import Bruteforce
from Modules.SubdomainFinder.Techniques.CTLogs import CTLogs
from Modules.SubdomainFinder.Techniques.DnsZoneTransfer import DnsZoneTransfer
from Modules.SubdomainFinder.Techniques.Hackertarget import Hackertarget
from Modules.SubdomainFinder.Techniques.WebArchive import WebArchive


class SubdomainFinder(Bruteforce, CTLogs, DnsZoneTransfer, Hackertarget, WebArchive):
    def __init__(self):
        super().__init__()
        self.subdomains = set()
        self._zone_transfer = True
        self._crt = True
        self._archive = True
        self._hackertarget = True
        self._bruteforce = False

    def add_subdomains(self, subdomains):
        subdomains = [self.raw_host(url) for url in subdomains]
        self.subdomains.update(subdomains)

    def get_subdomains(self):
        return self.subdomains

    def process(self):
        url = self.get_target()
        if self._zone_transfer:
            technique = DnsZoneTransfer()
            self.add_subdomains(technique.process(url))
        if self._crt:
            technique = CTLogs()
            self.add_subdomains(technique.process(url))
        if self._archive:
            technique = WebArchive()
            self.add_subdomains(technique.process(url))
        if self._hackertarget:
            technique = Hackertarget()
            self.add_subdomains(technique.process(url))
        if self._bruteforce:
            technique = Bruteforce()
            self.add_subdomains(technique.process(url))
        self.file_write("Unvalidated_subdomains.txt", self.get_subdomains())
        print(f"Found {len(self.get_subdomains())} subdomains. Results stored in {self.get_output_dir()}")

    def _set_zone_transfer(self, value):
        self._zone_transfer = value

    def _set_crt(self, value):
        self._crt = value

    def _set_archive(self, value):
        self._archive = value

    def _set_hackertarget(self, value):
        self._hackertarget = value

    def _set_brute_force(self, value):
        self._bruteforce = value
