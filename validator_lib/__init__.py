import os
import datetime
import platform


def find_validator_config_folder() -> str:
    """
    Find the configuration directory.
    Creates the directory if it does not exist.
    :return: The path to the configuration directory.
    """
    if platform.system() in {"Linux", "Darwin", "FreeBSD", "OpenBSD", "NetBSD"}:
        # .config folder in user home directory on Unix-like systems
        config_dir = os.path.join(
            os.path.expanduser("~"), ".config", "crl-serials-validator"
        )
    elif platform.system() == "Windows":
        # On Windows, use the AppData directory
        config_dir = os.path.join(
            os.path.expanduser("~"), "AppData", "Local", "crl-serials-validator"
        )
    elif platform.system() in {"Java", "iOS", "iPadOS", "Android"}:
        # no idea if this will work on these platforms
        config_dir = os.path.join(os.getcwd(), "data")
    else:
        # no idea if this will work ad no clue what the platform is
        config_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(config_dir, exist_ok=True)
    return config_dir


DOCS_URL = (
    "https://github.com/Center-for-Research-Libraries/validator/blob/main/README.md"
)
ERROR_GLOSSARY_URL = "https://github.com/Center-for-Research-Libraries/validator/blob/main/docs/disqualifying_issues.md"

CRL_FOLDER = os.path.join(os.path.expanduser("~"), "CRL")

VALIDATOR_INPUT_FOLDER = os.path.join(os.getcwd(), "input")
VALIDATOR_OUTPUT_FOLDER = os.path.join(os.getcwd(), "output")
VALIDATOR_DATA_FOLDER = find_validator_config_folder()
VALIDATOR_LOGS_FOLDER = os.path.join(os.getcwd(), "logs")

MARC_DB_NAME = "marc_collection.db"
ISSN_DB_NAME = "ISSN_db.db"
API_KEY_CONFIG_NAME = "api_keys.ini"
LOG_FILE_NAME = "validator_log_{:%Y-%m-%d}.log".format(datetime.datetime.now())

MARC_DB_LOCATION = os.path.join(CRL_FOLDER, MARC_DB_NAME)
API_KEY_CONFIG_LOCATION = os.path.join(CRL_FOLDER, API_KEY_CONFIG_NAME)
LOG_FILE_LOCATION = os.path.join(VALIDATOR_LOGS_FOLDER, LOG_FILE_NAME)

# Check if ISSN db is installed locally
if os.path.isfile(os.path.join(CRL_FOLDER, ISSN_DB_NAME)):
    ISSN_DB_LOCATION = os.path.join(CRL_FOLDER, ISSN_DB_NAME)
else:
    ISSN_DB_LOCATION = None
