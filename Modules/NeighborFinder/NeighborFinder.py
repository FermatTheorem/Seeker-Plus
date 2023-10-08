from Engine.Engine import Engine


class NeighborFinder(Engine):

    def __init__(self):
        super().__init__()
        self._neighbors = set()
        self._hackertarget_reverse_n = True
        self._hackertarget_api = True

    def process(self):
        if self._get_hackertarget_reverse() and self._hackertarget_api:
            self._hackertarget_reverse(self.get_target())
        self.file_write("Unvalidated_neighbors.txt", self._get_neighbors())
        print(f"Neighbor enumeration finished. Results stored in {self.get_output_dir()}")

    def _hackertarget_reverse(self, url):
        print("Enumerating websites nearby with Hackertarget...")
        ip = self.get_ip(url)
        if ip:
            url = f"https://api.hackertarget.com/reverseiplookup/?q={ip}"
            response = self.make_request(url, retries=5, keep_session=False)
            if not response:
                print("Unable to connect to Hackertarget")
            if response.status_code == 200:
                if 'API count exceeded' in response.text:
                    print("API count exceeded\n")  # todo: deal with api keys
                    self._hackertarget_api = False
                    return
                neighbors = list(set([self.raw_host(url) for url in response.text.split("\n")]))
                num = len(self._get_neighbors())
                self._add_neighbors(neighbors)
                print(f"Success! Found {len(self._get_neighbors()) - num} new websites nearby\n")
                return
            else:
                print(f"Unexpected status code: {response.status_code} ({url})")

    def _add_neighbors(self, neighbors):
        self._neighbors.update(neighbors)

    def _get_neighbors(self):
        return self._neighbors

    def _set_hackertarget_reverse(self, value):
        self._hackertarget_reverse_n = value

    def _get_hackertarget_reverse(self):
        return self._hackertarget_reverse_n
