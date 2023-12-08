import os

# Absolute path to the project root
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
#
# Log file full path
# LOG_FILE = ROOT_DIR + "/application.log"
#
# Selenium options
HEADLESS_BROWSER = True
BROWSER_OPTIONS = None

import yaml

with open("config.yaml", "r") as stream:
    try:
        CONFIG: dict = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)

CONFIG["General"]["root_directory"] = ROOT_DIR

CONFIG["General"]["output_directory"] = "/".join([
    CONFIG["General"]["root_directory"],
    CONFIG["General"]["output_directory"]
])

CONFIG["General"]["log_file"] = "/".join([
    CONFIG["General"]["output_directory"],
    CONFIG["General"]["log_file"]
])