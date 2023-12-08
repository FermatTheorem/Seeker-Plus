import logging
from config import CONFIG
from typing import Any
import os
import sys

_conf = CONFIG["General"]

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# File handler
file_handler = logging.FileHandler(_conf["log_file"])
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Stream handler (console)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

class Logger:

    def log_debug(self, message: Any) -> None:
        logger.debug(self._format_message(message))

    def log_info(self, message: Any) -> None:
        logger.info(self._format_message(message))

    def log_warning(self, message: Any) -> None:
        logger.warning(self._format_message(message))

    def log_error(self, message: Any) -> None:
        logger.error(self._format_message(message))

    def log_exception(self, message: Any) -> None:
        logger.exception(self._format_message(message))

    def _format_message(self, message: Any) -> str:
        frame = sys._getframe(2)
        caller_path = os.path.relpath(frame.f_code.co_filename, _conf["root_directory"])
        line_no = frame.f_lineno
        return f"{caller_path}:{line_no} - {message}"
