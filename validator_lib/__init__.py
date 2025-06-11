import os
import datetime
import platform
import logging
from termcolor import cprint, colored


MARC_DB_NAME = "marc_collection.db"
ISSN_DB_NAME = "ISSN_db.db"
API_KEY_CONFIG_NAME = "api_keys.ini"
LOG_FILE_NAME = "validator_log_{:%Y-%m-%d}.log".format(datetime.datetime.now())

# Set the variable below to True to force debug logging
DEBUG_MODE = True

CRL_FOLDER = os.path.join(os.path.expanduser("~"), "CRL")
VALIDATOR_INPUT_FOLDER = os.path.join(os.getcwd(), "input")
VALIDATOR_OUTPUT_FOLDER = os.path.join(os.getcwd(), "output")

VALIDATOR_LOGS_FOLDER = os.path.join(os.getcwd(), "logs")
LOG_FILE_LOCATION = os.path.join(VALIDATOR_LOGS_FOLDER, LOG_FILE_NAME)


def instantiate_folders() -> None:
    """
    Create the necessary folders for the validator.
    This includes the input, output, and logs folders.
    """
    for my_directory in [
        VALIDATOR_INPUT_FOLDER,
        VALIDATOR_OUTPUT_FOLDER,
        VALIDATOR_LOGS_FOLDER,
        CRL_FOLDER,
    ]:
        if not os.path.isdir(my_directory):
            logging.info("Creating directory {}".format(my_directory))
            os.mkdir(my_directory)


instantiate_folders()


def set_logging() -> None:
    """Initialize logging for the process."""
    if DEBUG_MODE is True:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(
        filename=LOG_FILE_LOCATION,
        level=log_level,
        filemode="a",
        format="%(asctime)s\t%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


set_logging()


def copy_old_validator_config_file() -> None:
    """
    Copy the old validator config file to the new location.
    This is used for migration of old installs.
    """
    old_folder = os.path.join(os.getcwd(), "data")
    old_file = os.path.join(old_folder, "config.yaml")

    if os.path.isfile(old_file):
        os.system("cls" if os.name == "nt" else "clear")
        logging.info(f"Need to migrate old config file at {old_file}.")
        new_folder = find_validator_config_folder()
        new_file = os.path.join(new_folder, "config.yaml")

        if not os.path.isfile(new_file):
            os.makedirs(new_folder, exist_ok=True)
            with open(old_file, "r") as old_config:
                with open(new_file, "w") as new_config:
                    new_config.write(old_config.read())
            logging.info(f"Migrated old config file from {old_folder} to {new_file}")
            cprint("Migrating old config file...", "green")
            print("")
            print(f"{colored('from:', 'green')} {old_file}")
            print(f"{colored('to:  ', 'green')} {new_file}")
            print("")
            cprint("The old config file will be deleted.", "yellow")
            print("")

            os.remove(old_file)
            logging.info(f"Deleted old config file at {old_file}")
            gitkeep = os.path.join(old_folder, ".gitkeep")
            if os.path.isfile(gitkeep):
                os.remove(gitkeep)
                logging.info(f"Deleted old .gitkeep file at {gitkeep}")

            jstor_files = os.listdir(old_folder)
            for jstor_file in jstor_files:
                if jstor_file.lower().startswith("jstor_"):
                    jstor_file_path = os.path.join(old_folder, jstor_file)
                    new_jstor_file_path = os.path.join(CRL_FOLDER, jstor_file)

                    if not os.path.isfile(new_jstor_file_path):
                        os.rename(jstor_file_path, new_jstor_file_path)
                        msg = f"Migrated old JSTOR file from {jstor_file_path} to {new_jstor_file_path}"
                        logging.info(msg)
                        cprint(msg, "green")
                        print("")

            myfiles = os.listdir(old_folder)

            if myfiles:
                cprint(
                    "The old configuration data folder is not empty so it will not be deleted.",
                    "yellow",
                )
                print("")
            else:
                os.rmdir(old_folder)
                logging.info(f"Deleted old data folder at {old_folder}")
                cprint("Deleting empty old configuration data folder.", "green")
                print("")
            cprint("THIS WAS A ONE-TIME MIGRATION.", "green")
            print("")

            input("Press Enter to continue.")


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

copy_old_validator_config_file()
VALIDATOR_CONFIG_FOLDER = find_validator_config_folder()

API_KEY_CONFIG_LOCATION = os.path.join(CRL_FOLDER, API_KEY_CONFIG_NAME)

MARC_DB_LOCATION = os.path.join(CRL_FOLDER, MARC_DB_NAME)

# Check if ISSN db is installed locally
if os.path.isfile(os.path.join(CRL_FOLDER, ISSN_DB_NAME)):
    ISSN_DB_LOCATION = os.path.join(CRL_FOLDER, ISSN_DB_NAME)
else:
    ISSN_DB_LOCATION = None
