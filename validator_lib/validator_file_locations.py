"""
Find the directories containing the ISSN dataase (if installed), the local MARC database, and the configuration
file containing API keys.

In most installations of the Validator these will all be in the data folder of the Validator's main directory.
They will only appear in other places if the user also uses other CRL applications (most notably the CRL MARC Machine) or if the user installed the Validator prior to September 13, 2021.

The ISSN database can also appear in a specific internal location if the Validator is used inside CRL's network.

To force the Validator to only use the data folder in the main validator directory, pass True as an argument
called portable_install to ValidatorFileLocations.

Right now this treats systems running on Windows Subsystem for Linux (WSL) as Linux machines, and will look for 
and store data in the Linux directory structure.
"""

import os
import platform
from appdirs import AppDirs
import logging


class ValidatorFileLocations:

    current_os = platform.system()
    home_folder = os.path.expanduser("~")
    crl_folder = os.path.join(os.path.expanduser("~"), 'CRL')
    marc_db_name = 'marc_collection.db'
    issn_db_name = 'ISSN_db.db'
    api_key_config_name = 'api_keys.ini'

    validator_input_folder = os.path.join(os.getcwd(), 'input')
    validator_output_folder = os.path.join(os.getcwd(), 'output')
    validator_data_folder = os.path.join(os.getcwd(), 'data')
    validator_logs_folder = os.path.join(os.getcwd(), 'logs')

    input_files = []

    data_storage_folder = None
    marc_db_location = None
    issn_db_location = None

    def __init__(self, portable_install=False):
        self.initialize_folders()

        self.portable_install = portable_install

        self.issn_db_folder = None
        self.marc_db_folder = None

        self.get_marc_and_issn_data_locations()

        if not self.data_storage_folder:
            self.data_storage_folder = self.validator_data_folder

        self.check_about_file()
        self.get_input_files()

    def get_marc_and_issn_data_locations(self):
        """
        Look for the MARC database (and optional ISSN database) in various standard locations. If not found, set them
        in the default location. For portable installs that will be the data folder of the Validator. For everything else
        this will be the user data directory as defined by the appdirs library.
        """
        self.look_for_validator_data_folder()

        if self.portable_install:
            self.marc_db_folder = self.validator_data_folder
        else:
            self.look_for_crl_marc_machine_folder()
            self.look_for_crl_folder()
            self.look_for_user_data_dir()

            if not self.marc_db_folder:
                self.make_user_data_dir()

            if self.marc_db_folder:
                self.data_storage_folder = self.marc_db_folder
            elif self.issn_db_folder:
                self.data_storage_folder = self.issn_db_folder
                self.marc_db_folder = self.issn_db_folder

            self.marc_db_location = os.path.join(self.marc_db_folder, self.marc_db_name)

    def log_file_location_results(self):
        logging.info('Data storage folder at {}'.format(self.data_storage_folder))
        if self.marc_db_location:
            logging.info('Found MARC database at {}'.format(self.marc_db_location))
        else:
            logging.info('MARC database not found.')
        if self.issn_db_location:
            logging.info('Found ISSN database at {}'.format(self.issn_db_location))
        else:
            logging.info('ISSN database not found.')

    def check_folder(self, dir):
        if not os.path.isdir(dir):
            return
        dir_list = os.listdir(dir)
        self.check_for_marc_db(dir, dir_list)
        self.check_for_issn_db(dir, dir_list)

    def check_for_marc_db(self, dir, dir_list):
        if not self.marc_db_location and self.marc_db_name in dir_list:
            self.marc_db_folder = dir

    def check_for_issn_db(self, dir, dir_list):
        if not self.issn_db_location and self.issn_db_name in dir_list:
            self.issn_db_folder = dir
            self.issn_db_location = os.path.join(dir, self.issn_db_name)

    def look_for_validator_data_folder(self):
        self.check_folder(self.validator_data_folder)

    def look_for_crl_marc_machine_folder(self):
        marc_machine_folder = os.path.join(self.home_folder, 'CRL MARC Machine')
        self.check_folder(marc_machine_folder)

    def look_for_crl_folder(self):
        self.check_folder(self.crl_folder)

    def _get_appidirs_user_data_directory(self):
        if self.current_os == 'Windows':
            a = AppDirs(appname='CRL')
        elif self.current_os == 'Linux':
            a = AppDirs(appname='CRL')
        elif self.current_os == 'Darwin':
            # This might be wrong; don't have access to a MacOS computer to test with
            a = AppDirs(appname='CRL')
        return a.user_data_dir

    def look_for_user_data_dir(self):
        """
        The plan now is to store any new system-wide databases in the user's data directory in a 
        subdiectory called CRL. On Linux this requires and app name of "CRL". On Windows the top folder level
        is the app author, and an app name would be a lower level if we added it.
        """
        user_data_dir = self._get_appidirs_user_data_directory()
        self.check_folder(user_data_dir)

    def make_user_data_dir(self):
        user_data_dir = self._get_appidirs_user_data_directory()
        try:
            os.makedirs(user_data_dir, exist_ok=True)
            self.marc_db_folder = user_data_dir
        except PermissionError:
            logging.warning("Don't have permission to create user data directory at {}. Using data folder in main program folder.".format(user_data_dir))
            self.marc_db_folder = self.validator_data_folder

    def get_input_files(self):
        all_input_files = os.listdir(self.validator_input_folder)
        for input_file in all_input_files:
            if input_file.startswith('~'):
                continue
            if not input_file.endswith('mrk') and not input_file.endswith('mrc'):
                if not input_file.endswith('txt') and not input_file.endswith('csv') and not input_file.endswith('tsv'):
                    if not input_file.endswith('xlsx'):
                        continue
            self.input_files.append(input_file)

    def initialize_folders(self):
        if not os.path.isdir(self.validator_input_folder):
            logging.info('Creating input directory.')
            os.mkdir(self.validator_input_folder)
        if not os.path.isdir(self.validator_output_folder):
            logging.info('Creating output directory.')
            os.mkdir(self.validator_output_folder)
        if not os.path.isdir(self.validator_input_folder):
            logging.info('Creating data directory.')
            os.mkdir(self.validator_data_folder)
        if not os.path.isdir(self.validator_logs_folder):
            logging.info('Creating logs directory.')
            os.mkdir(self.validator_logs_folder)

    def check_about_file(self):
        """
        Add a basic about file to our data folder. If the data folder is in the main application folder then skip this step.
        """
        if self.data_storage_folder != self.validator_data_folder:
            about_file_location = os.path.join(self.data_storage_folder, 'about.txt')
            if not os.path.isfile(about_file_location):
                with open(about_file_location, 'w') as fout:
                    fout.write('This folder contains data files for utilities from the Center for Research Libraries.\n')


def print_validator_file_locations():
    from termcolor import colored, cprint
    import colorama
    
    file_locations = ValidatorFileLocations()

    colorama.init()

    name_color = 'blue'
    highlight_color = 'yellow'
    location_color = 'green'
    not_installed_color = 'red'

    header = '~~~~~~~~~~~~~~\n'
    header += 'FILE LOCATIONS\n'
    header += '~~~~~~~~~~~~~~'
    cprint(header, highlight_color)
    main_data_folder = colored('main data folder', name_color)
    local_marc_database = colored('local MARC database', name_color)
    issn_database = colored('ISSN database', name_color)
    not_installed = colored('not installed', not_installed_color)

    print('The {} is located at: '.format(main_data_folder), end='')
    cprint(file_locations.data_storage_folder, location_color)
    print('The {} is located at: '.format(local_marc_database), end='')
    cprint(file_locations.marc_db_location, location_color)
    if file_locations.issn_db_location:
        print('The {} is located at: '.format(issn_database), end='')
        cprint(file_locations.issn_db_location, location_color)
    else:
        print('The {} is {}.'.format(issn_database, not_installed))
