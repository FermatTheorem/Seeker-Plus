import asyncio
import random
import string
from typing import AsyncGenerator, Optional, Dict, List, Set
import dns.asyncresolver
import dns.exception
import dns.name
from dns.rdtypes.IN.A import A
from dns.rdtypes.IN.AAAA import AAAA

from Engine.Engine import Engine

_WILDCARD_PROBES: int = 3
_MAX_CONCURRENT_TASKS: int = 50  # Limiting the number of concurrent tasks


class Bruteforce(Engine):
    _wordlist_path: str = "Misc/subdomains-top1million-5000.txt"
    _potential_subdomains: List[str] = []
    _dns_resolver: dns.asyncresolver.Resolver = dns.asyncresolver.Resolver()
    _concurrency_semaphore: asyncio.Semaphore = asyncio.Semaphore(value=_MAX_CONCURRENT_TASKS)
    _wildcard_addresses: Optional[Set[str]] = None
    _subdomains_checked_count: int = 0
    _found_subdomains: Set[str] = set()
    _dns_servers: List[str] = [
        "8.8.8.8",  # Google Primary DNS
        "8.8.4.4",  # Google Secondary DNS
        "1.1.1.1",  # Cloudflare Primary DNS
        "1.0.0.1",  # Cloudflare Secondary DNS
        "9.9.9.9",  # Quad9 Primary DNS
        "149.112.112.112",  # Quad9 Secondary DNS
    ]

    def __init__(self):
        self._populate_subdomains_from_wordlist()

    def _populate_subdomains_from_wordlist(self) -> None:
        with self.open_file(self._wordlist_path) as file:
            for line in file:
                self._potential_subdomains.append(line.strip())
        self.log_info(f"Read {len(self._potential_subdomains)} lines from {self._wordlist_path}")

    def process(self, url: str) -> Set[str]:
        asyncio.run(self._process(self.raw_host(url)))
        return self._found_subdomains

    async def _process(self, url: str) -> None:
        log_task = asyncio.create_task(self._log_progress())
        try:
            async for subdomain in self._enumerate_subdomains(url):
                if subdomain:
                    self._found_subdomains.add(subdomain["name"])
        finally:
            log_task.cancel()

    async def _enumerate_subdomains(self, url: str) -> AsyncGenerator[str, None]:
        self.log_info(f"Starting subdomain bruteforce for {url}")
        await self._initialize_wildcard(url)
        self.log_info(f"Initialized wildcard: {self._wildcard_addresses}")
        async for subdomain in self._bruteforce_subdomains(dns.name.from_text(url)):
            yield subdomain

    async def _initialize_wildcard(self, domain: str) -> None:
        self.log_info(f"Initializing wildcard for {domain}")
        domain_name = dns.name.from_text(domain)
        self._wildcard_addresses = await self._detect_wildcard(domain_name)

    async def _detect_wildcard(self, domain: dns.name.Name) -> Set[str]:
        self.log_info(f"Detecting wildcard for {domain}")
        random_labels = [self._random_string() for _ in range(_WILDCARD_PROBES)]
        wildcard_detection_tasks = [self._attempt_resolution(domain, label, wildcard_ok=True) for label in
                                    random_labels]
        wildcard_addresses = set()
        for task in asyncio.as_completed(wildcard_detection_tasks):
            if subdomain_info := await task:
                wildcard_addresses.update(subdomain_info['ip_addresses'])
        return wildcard_addresses

    async def _bruteforce_subdomains(self, domain: dns.name.Name) -> AsyncGenerator[Dict[str, List[str]], None]:
        self.log_info(f"Bruteforcing subdomains for {domain}")
        tasks = set()
        for label in self._potential_subdomains:
            task = asyncio.ensure_future(self._attempt_resolution(domain, label, wildcard_ok=False))
            tasks.add(task)

            if len(tasks) >= _MAX_CONCURRENT_TASKS:
                done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for result in done:
                    subdomain_info = await result
                    if subdomain_info:
                        self.log_info(f"Found subdomain: {subdomain_info}")
                    yield subdomain_info

        for task in asyncio.as_completed(tasks):
            subdomain_info = await task
            if subdomain_info:
                self.log_info(f"Found subdomain: {subdomain_info}")
            yield subdomain_info

    async def _attempt_resolution(self, domain: dns.name.Name, label: str, *, wildcard_ok: bool) -> Optional[
        Dict[str, List[str]]]:
        subdomain_candidate = dns.name.from_text(label, origin=domain)
        self._subdomains_checked_count += 1
        return await self._resolve_subdomain(subdomain_candidate, wildcard_ok=wildcard_ok)

    async def _resolve_subdomain(self, domain: dns.name.Name, *, wildcard_ok: bool) -> Optional[Dict[str, List[str]]]:
        async with self._concurrency_semaphore:
            try:
                selected_dns_server = random.choice(self._dns_servers)
                self._dns_resolver.nameservers = [selected_dns_server]
                dns_query_answers = await self._dns_resolver.resolve(str(domain), 'A')
            except dns.exception.DNSException:
                return None

        ip_addresses = self._get_ip_addresses(dns_query_answers)
        if not wildcard_ok and self._wildcard_addresses is not None:
            ip_addresses = [ip for ip in ip_addresses if ip not in self._wildcard_addresses]
            if not ip_addresses:
                return None

        return {'name': domain.to_text(omit_final_dot=True), 'ip_addresses': ip_addresses}

    async def _log_progress(self) -> None:
        while True:
            self.log_info(f"Checked {self._subdomains_checked_count}/{len(self._potential_subdomains)} subdomains")
            await asyncio.sleep(10)

    def _get_ip_addresses(self, answers: dns.resolver.Answer) -> List[str]:
        ip_addresses = []
        for record in answers.rrset:
            if isinstance(record, (A, AAAA)):
                ip_addresses.append(record.to_text())
        return ip_addresses

    def _random_string(self) -> str:
        alpha = string.ascii_lowercase + string.digits
        label_length = random.randint(16, 32)
        return "".join(random.choice(alpha) for _ in range(label_length))
