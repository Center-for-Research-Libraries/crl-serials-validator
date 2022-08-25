"""
A library for finding CRL databases and data files, as well as the default
data folder.
"""

import os
import getpass
import platform
import sys

try:
    from termcolor import colored
except ModuleNotFoundError:
    def colored(input_string, *args):
        return input_string

# Add a DEFAULT_USERNAME on a system where files will be stored somewhere other
# than the logged-in user's home directory. This will most commonly be used on
# web servers, where the "user" will be a process called "web" or the like
DEFAULT_USERNAME = None
DATA_FOLDER_NAME = 'CRL'
MARC_MACHINE_FOLDER_NAME = 'CRL MARC Machine'
MARC_DB_NAME = 'marc_collection.db'
ISSN_DB_NAME = 'ISSN_db.db'
API_KEY_CONFIG_FILENAME = 'api_keys.yaml'
HOLDERS_API_DB_FILENAME = 'holders_from_api.db'
CRL_CATALOG_FILENAME = 'crl_full_catalog.mrk'


class CrlFileLocations:
    """
    Find CRL database and data files.

    At object creation pass a variable data_folder_path to force all locations 
    to a specific folder.
    """

    current_os = platform.system()

    def __init__(self, data_folder_path: str = '', fallback_location: str = '') -> None:
        """
        Defaults to a directory called "CRL" in the user's home directory.
        Most data will be stored there.
        """
        self.files = {}
        self.locations = {}

        self.default_location = data_folder_path
        self.fallback_location = fallback_location

        self.username = getpass.getuser()
        self.locations['HOME_FOLDER'] = os.path.expanduser("~")

        if DEFAULT_USERNAME:
            self.username = DEFAULT_USERNAME
            self.locations['HOME_FOLDER'] = os.path.join(
                os.path.split(self.locations['HOME_FOLDER'])[0], self.username)

        if self.current_os == 'Windows' and self.locations['HOME_FOLDER'].startswith('H:'):
            # work around -- CRL home sometimes set to H drive
            self.locations['HOME_FOLDER'] = os.path.join('C:\\Users', self.username)
        elif self.current_os == 'Linux':
            self.check_for_wsl_on_windows()

        self.locations['DATA_FOLDER'] = self.find_data_folder()

        self.files['MARC_DB'] = os.path.join(self.locations['DATA_FOLDER'], MARC_DB_NAME)
        self.files['ISSN_DB'] = os.path.join(self.locations['DATA_FOLDER'], ISSN_DB_NAME)
        self.files['API_KEY_CONFIG_FILE'] = os.path.join(self.locations['DATA_FOLDER'], API_KEY_CONFIG_FILENAME)
        self.files['HOLDERS_API_DB'] = os.path.join(self.locations['DATA_FOLDER'], HOLDERS_API_DB_FILENAME)
        self.files['CRL_CATALOG'] = os.path.join(self.locations['DATA_FOLDER'], CRL_CATALOG_FILENAME)

    def find_data_folder(self) -> str:
        if self.default_location:
            return self.default_location
        
        crl_folder = os.path.join(self.locations['HOME_FOLDER'], DATA_FOLDER_NAME)
        if os.path.isdir(crl_folder):
            return crl_folder
        
        marc_machine_folder = os.path.join(
            self.locations['HOME_FOLDER'], MARC_MACHINE_FOLDER_NAME)
        if os.path.isdir(marc_machine_folder):
            return marc_machine_folder

        if self.fallback_location:
            return self.fallback_location

        try:
            os.mkdir(crl_folder)
        except (FileNotFoundError, PermissionError):
            sys.exit(f'Failed attempt to make data directory at {crl_folder}')

        return crl_folder

    def check_for_wsl_on_windows(self) -> None:
        """
        TODO: this is incomplete
        With systems using WSL, we'll try to use the data folder in the Windows 
        home directory. This method depends on the user having the same WSL and 
        Windows usernames.

        Note that getpass doesn't work on Windows, which is why it's only 
        imported if the system detects a Linux install.
        """
        windows_home_folder = os.path.join('/mnt/c/Users', self.username)

        if os.path.isdir(windows_home_folder):
            self.locations['HOME_FOLDER'] = windows_home_folder


def get_marc_db_location(data_folder_path: str = '', fallback_location: str = '') -> str:
    """
    Find MARC db location, creating one if none exits.
    """
    locs = CrlFileLocations(
        data_folder_path=data_folder_path, fallback_location=fallback_location)
    return locs.files['MARC_DB']


def get_issn_db_location(data_folder_path: str = '', fallback_location: str = '') -> str:
    """
    Get ISSN db location.
    """
    locs = CrlFileLocations(
        data_folder_path=data_folder_path, fallback_location=fallback_location)
    return locs.files['ISSN_DB']


def get_api_key_file_location(data_folder_path: str = '', fallback_location: str = '') -> str:
    """
    Find API key file, creating one if none exists.
    """
    locs = CrlFileLocations(
        data_folder_path=data_folder_path, fallback_location=fallback_location)
    return locs.files['API_KEY_CONFIG_FILE']


def get_crl_catalog_location(data_folder_path: str = '', fallback_location: str = '') -> str:
    """
    Get CRL catalog file location.
    """
    locs = CrlFileLocations(
        data_folder_path=data_folder_path, fallback_location=fallback_location)
    return locs.files['CRL_CATALOG']


def get_holders_api_db_location(data_folder_path: str = '', fallback_location: str = '') -> str:
    """
    Get the local database of data from the holdings API
    """
    locs = CrlFileLocations(
        data_folder_path=data_folder_path, fallback_location=fallback_location)
    return locs.files['HOLDERS_API_DB']


def check_if_file_exists(wanted_file):
    found = '         '
    if not os.path.isfile(wanted_file) and not os.path.isdir(wanted_file):
        found = colored('NOT FOUND', 'red', 'on_white')
    return found


def print_crl_locations() -> None:
    """
    Print a list of all locations.
    """
    crl_locations = ['HOME_FOLDER', 'DATA_FOLDER']
    crl_files = [
        'MARC_DB', 'ISSN_DB', 'API_KEY_CONFIG_FILE', 'HOLDERS_API_DB', 'CRL_CATALOG'
    ]

    locs = CrlFileLocations()

    print(f'{colored(locs.current_os, "yellow")} OS')

    for crl_location in crl_locations:
        found = check_if_file_exists(locs.locations[crl_location])
        crl_location_data = colored(locs.locations[crl_location], 'yellow')
        print(f'{crl_location:<19} {found} {crl_location_data}')

    for crl_file in crl_files:
        found = check_if_file_exists(locs.files[crl_file])
        crl_file_data = colored(locs.files[crl_file], 'yellow')
        print(f'{crl_file:<19} {found} {crl_file_data}')


if __name__ == "__main__":
    print_crl_locations()
