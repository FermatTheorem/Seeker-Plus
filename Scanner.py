from SubDomainFinder import SubDomainFinder
from NeighborFinder import NeighborFinder

class Scanner(SubDomainFinder, NeighborFinder):

    def __init__(self):
        super().__init__()