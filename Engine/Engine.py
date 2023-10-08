from .RequestHadler import RequestHandler
from .FileHandler import FileHandler

class Engine(RequestHandler, FileHandler):
    def __init__(self):
        super().__init__()