import logging
import os
import sys
from config import CONFIG
from .FileHandler import FileHandler


class Logger:
    module_name = 'default_module'  # if someone runs a module outside of Seeker.py
    loggers = {}

    @classmethod
    def _get_logger(cls, module_name):
        if module_name not in cls.loggers:
            cls.loggers[module_name] = cls._create_logger(module_name)
        return cls.loggers[module_name]

    @staticmethod
    def _create_logger(module_name):
        logger = logging.getLogger(module_name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False  # Prevents duplicate logging

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        output_dir = FileHandler.get_output_dir()

        # Console Handlers
        ch_info = logging.StreamHandler(stream=sys.stdout)
        ch_info.setFormatter(formatter)
        ch_info.addFilter(lambda record: record.levelno <= logging.INFO)
        logger.addHandler(ch_info)

        ch_error = logging.StreamHandler(stream=sys.stderr)
        ch_error.setFormatter(formatter)
        ch_error.addFilter(lambda record: record.levelno >= logging.WARNING)
        logger.addHandler(ch_error)

        # File Handlers for application.log and module-specific log
        fh = logging.FileHandler(f'{output_dir}/application.log')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        if module_name != 'error':
            mh = logging.FileHandler(f'{output_dir}/{module_name}.log')
            mh.setFormatter(formatter)
            logger.addHandler(mh)

        # Separate handler for error.log
        if module_name == 'error':
            eh = logging.FileHandler(f'{output_dir}/error.log')
            eh.setFormatter(formatter)
            logger.addHandler(eh)

        return logger

    @staticmethod
    def _format_message(message):
        frame = sys._getframe(2)
        caller_path = os.path.relpath(frame.f_code.co_filename, CONFIG["General"]["root_directory"])
        line_no = frame.f_lineno
        return f"{caller_path}:{line_no} - {message}"

    @classmethod
    def log_debug(cls, message):
        logger = cls._get_logger(cls.logger.module_name)
        logger.debug(cls._format_message(message))

    @classmethod
    def log_info(cls, message):
        logger = cls._get_logger(cls.logger.module_name)
        logger.info(cls._format_message(message))

    @classmethod
    def log_warning(cls, message):
        logger = cls._get_logger(cls.logger.module_name)
        logger.warning(cls._format_message(message))
        error_logger = cls._get_logger('error')
        error_logger.warning(cls._format_message(message))

    @classmethod
    def log_error(cls, message):
        logger = cls._get_logger(cls.logger.module_name)
        logger.error(cls._format_message(message))
        error_logger = cls._get_logger('error')
        error_logger.error(cls._format_message(message))

    @classmethod
    def log_exception(cls, message):
        logger = cls._get_logger(cls.logger.module_name)
        logger.exception(cls._format_message(message))
        error_logger = cls._get_logger('error')
        error_logger.exception(cls._format_message(message))

