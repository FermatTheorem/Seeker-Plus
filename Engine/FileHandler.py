import os
from typing import Iterable, Union


class FileHandler:
    def __init__(self) -> None:
        self.output_dir: str = ""

    def set_output_dir(self, value: str) -> None:
        self.output_dir = value

    def get_output_dir(self) -> str | None:
        return self.output_dir

    def file_write(self, filename: str, content: Union[str, Iterable[str]]) -> None:
        if not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir)
            except OSError as e:
                raise RuntimeError(f"Failed to create directory {self.output_dir}: {str(e)}")
        full_path = os.path.join(self.output_dir, filename)

        try:
            with open(full_path, "w", encoding="utf-8") as file:
                if isinstance(content, str):
                    file.write(content)
                elif isinstance(content, Iterable):
                    for line in content:
                        file.write(line + "\n")
                else:
                    raise ValueError("Content must be an iterable or a string.")
        except Exception as e:
            raise RuntimeError(f"Failed to write to {full_path}: {str(e)}")

# # Example usage:
# if __name__ == "__main__":
#     handler = FileHandler()
#     handler.set_output_dir("output_directory")  # Set the output directory
#
#     content = ["Line 1", "Line 2", "Line 3"]
#
#     try:
#         handler.file_write("output.txt", content)
#         print("File written successfully.")
#     except Exception as e:
#         print(f"An error occurred: {str(e)}")
