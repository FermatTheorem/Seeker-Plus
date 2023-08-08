from SuperClass import SuperClass

class NeighborFinder(SuperClass):

    def __init__(self):
        super().__init__()
        self.neighbors = set()
        self.hackertargetReverseN = True

    def neighborProcess(self, url):
        if self.getHackertargetReverse():
            self.hackertargetReverse(url)

    def hackertargetReverse(self, url):
        print("Enumerating websites nearby with Hackertarget...")
        IP = self.getIP(url)
        if IP:
            url = f"https://api.hackertarget.com/reverseiplookup/?q={IP}"
            response = self.makeRequest(url, retries=5, keep_session=False)
            if not response:
                print("Unable to connect to Hackertarget")
            if response.status_code == 200:
                if 'API count exceeded' in response.text:
                    print("API count exceeded\n") #todo: deal with api keys
                    return
                neighbors = list(set([self.rawHost(url) for url in response.text.split("\n")]))
                num = len(self.getNeighbors())
                self.addNeighbors(neighbors)
                print(f"Success! Found {len(self.getNeighbors()) - num} new websites nearby\n")
                return
            else:
                print(f"Unexpected status code: {response.status_code} ({url})")

    def addNeighbors(self, neighbors):
        self.neighbors.update(neighbors)

    def getNeighbors(self):
        return self.neighbors

    def setHackertargetReverse(self, value):
        self.hackertargetReverseN = value

    def getHackertargetReverse(self):
        return self.hackertargetReverseN