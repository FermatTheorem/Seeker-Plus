import logging


class Logger:
    def __init__(self, log_file: str = 'application.log') -> None:
        self.log_file: str = log_file
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        file_handler: logging.FileHandler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        formatter: logging.Formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def log_info(self, message: str) -> None:
        self.logger.info(message)

    def log_error(self, message: str) -> None:
        self.logger.error(message)

    def log_warning(self, message: str) -> None:
        self.logger.warning(message)

    def log_exception(self, message: str) -> None:
        self.logger.exception(message)
