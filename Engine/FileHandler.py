import os
from typing import Iterable
from config import CONFIG


class FileHandler:

    @staticmethod
    def set_output_dir(value: str) -> None:
        if not isinstance(CONFIG.get("General", None), dict):
            CONFIG["General"] = {}
        CONFIG["General"]["output_directory"] = value

    @staticmethod
    def get_output_dir() -> str:
        output_dir = CONFIG.get("General", {}).get("output_directory", None)
        return "Output" if not output_dir else output_dir

    @staticmethod
    def file_write(filename: str, content: str | Iterable[str], output_directory: str = None) -> None:
        output_dir = FileHandler.get_output_dir() if not output_directory else output_directory
        if not output_dir or not isinstance(output_dir, str):
            raise ValueError("Output directory must be a non-empty string")

        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError as e:
                raise RuntimeError(f"Failed to create directory {output_dir}: {str(e)}")
        full_path = os.path.join(output_dir, filename)

        try:
            with open(full_path, "w", encoding="utf-8") as file:
                if isinstance(content, str):
                    file.write(content)
                elif isinstance(content, Iterable):
                    for line in content:
                        file.write(line + "\n")
                else:
                    raise ValueError("Content must be an iterable or a string")
        except Exception as e:
            raise RuntimeError(f"Failed to write to {full_path}: {str(e)}")

    @staticmethod
    def open_file(filename: str, folder: str = "", mode: str = "r", encoding: str = "utf-8"):
        if not filename or not isinstance(filename, str) or not isinstance(folder, str):
            raise ValueError("Unable open a file. Both filename and folder must be a string")

        folder = folder if folder.startswith("/") else "/".join([CONFIG["General"]["root_directory"], folder])
        fullname = filename if filename.startswith("/") else "/".join([folder, filename])

        if not os.path.exists(fullname) or not os.path.isfile(fullname):
            raise RuntimeError(f"'{fullname}' doesn't exist or is not a file")

        return open(fullname, mode=mode, encoding=encoding)
