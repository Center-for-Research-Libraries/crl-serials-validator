"""
A few functions relating to the locations of files and folders the Validator
uses.
"""

import os
import logging
import shutil
from termcolor import cprint, colored
import colorama

from validator_lib import (
    VALIDATOR_INPUT_FOLDER,
    VALIDATOR_OUTPUT_FOLDER,
    VALIDATOR_CONFIG_FOLDER,
    VALIDATOR_LOGS_FOLDER,
    CRL_FOLDER,
    MARC_DB_LOCATION,
    ISSN_DB_LOCATION,
)


def print_validator_file_locations():
    """
    Print the location of the MARC and ISSN databases to the command line.

    This function is triggered by running the Validator with a -f flag, like so:
        python crl_serials_validator.py -f
    """

    colorama.init()

    name_color = "cyan"
    highlight_color = "yellow"
    location_color = "green"
    not_installed_color = "red"

    header = "~~~~~~~~~~~~~~\n"
    header += "FILE LOCATIONS\n"
    header += "~~~~~~~~~~~~~~"
    cprint(header, highlight_color)
    main_data_folder = colored("main data folder", name_color)
    local_marc_database = colored("local MARC database", name_color)
    issn_database = colored("ISSN database", name_color)
    not_installed = colored("not installed", not_installed_color, "on_white")

    print("The {} is located at: ".format(main_data_folder), end="")
    cprint(CRL_FOLDER, location_color)
    if os.path.isfile(MARC_DB_LOCATION):
        print("The {} is located at: ".format(local_marc_database), end="")
        cprint(MARC_DB_LOCATION, location_color)
    else:
        print("The {} has not been created.".format(local_marc_database))
    if ISSN_DB_LOCATION:
        print("The {} is located at: ".format(issn_database), end="")
        cprint(ISSN_DB_LOCATION, location_color)
    else:
        print("The {} is {}.".format(issn_database, not_installed))


def migrate_from_appdirs_directory():
    """
    Older installations will have the databases and related files placed in the
    folder chosen by the appdirs library. Search for these and migrate them to a
    "CRL" folder in the user's home directory.

    This functions was finalized 2022-02-18. Soon there should be no more
    installations using the appdirs folder, at which point it can be removed.

    I've removed appdirs from the requirements for the project, on the
    assumption that a Python installation without appdirs already installed
    won't have Validator folders in the locations specified by appdirs. If
    appdirs isn't found, this function should abort and return to the main
    process.
    """
    try:
        from appdirs import AppDirs
    except ImportError:
        return

    appdirs_directory = AppDirs(appname="CRL").user_data_dir
    print(appdirs_directory)
    if not os.path.isdir(appdirs_directory):
        return

    cprint("Performing one-time migration of files.", "yellow")
    print("Source:      {}".format(colored(appdirs_directory, "cyan")))
    print("Destination: {}".format(colored(CRL_FOLDER, "cyan")))
    if not os.path.isdir(CRL_FOLDER):
        # No CRL folder, so we can cleanly move the whole appdirs folder
        shutil.move(appdirs_directory, CRL_FOLDER)
    else:
        # CRL folder exists. Copy file-by-file.
        appdirs_contents = os.listdir(appdirs_directory)
        for my_file in appdirs_contents:
            source = os.path.join(appdirs_directory, my_file)
            destination = os.path.join(CRL_FOLDER, my_file)
            shutil.move(source, destination)
        os.rmdir(appdirs_directory)
