from .HttpClient import RequestHandler
from .FileHandler import FileHandler

class Engine(RequestHandler, FileHandler):
    pass