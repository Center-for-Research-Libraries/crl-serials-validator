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
import logging

from validator_lib.validator_data import *


def initialize_validator_folders():

    for my_directory in [VALIDATOR_INPUT_FOLDER, VALIDATOR_OUTPUT_FOLDER, VALIDATOR_DATA_FOLDER, VALIDATOR_LOGS_FOLDER]:
        if not os.path.isdir(my_directory):
            logging.info('Creating directory {}'.format(my_directory))
            os.mkdir(my_directory)


class ValidatorFileLocations:

    def __init__(self, portable_install=False):

        self.portable_install = portable_install

        self.input_files = []

        self.issn_db_folder = None
        self.marc_db_folder = None
        self.data_storage_folder = None
        self.marc_db_location = None
        self.issn_db_location = None

        self.find_marc_database_location()
        self.find_issn_database_location()

        if not self.data_storage_folder:
            self.data_storage_folder = self.validator_data_folder

        self.add_about_file()
        self.get_input_files()

    def find_marc_database_location(self):
        """
        Look for the MARC database (and optional ISSN database) in various standard locations. If not found, set them
        in the default location. For portable installs that will be the data folder of the Validator. For everything else
        this will be the user data directory as defined by the appdirs library.
        """
        if self.portable_install is True:
            self.marc_db_folder = VALIDATOR_DATA_FOLDER
            self.marc_db_location = os.path.join(VALIDATOR_DATA_FOLDER, MARC_DB_NAME)
        elif os.path.isdir(APPDIRS_DIRECTORY) and os.path.isfile(os.path.join(APPDIRS_DIRECTORY, MARC_DB_NAME)):
            self.marc_db_folder = APPDIRS_DIRECTORY
            self.marc_db_location = (os.path.join(APPDIRS_DIRECTORY, MARC_DB_NAME))
        elif os.path.isdir(CRL_FOLDER) and os.path.isfile(os.path.join(CRL_FOLDER, MARC_DB_NAME)):
            self.marc_db_folder = CRL_FOLDER
            self.marc_db_location = (os.path.join(CRL_FOLDER, MARC_DB_NAME))
        else:
            if not os.path.isdir(APPDIRS_DIRECTORY):
                os.mkdir(APPDIRS_DIRECTORY)
            self.marc_db_folder = APPDIRS_DIRECTORY
            self.marc_db_location = (os.path.join(APPDIRS_DIRECTORY, MARC_DB_NAME))

        self.data_storage_folder = self.marc_db_folder
        self.add_about_file()

    def find_issn_database_location(self):
        if os.path.isdir(APPDIRS_DIRECTORY) and os.path.isfile(os.path.join(APPDIRS_DIRECTORY, ISSN_DB_NAME)):
            self.issn_db_folder = APPDIRS_DIRECTORY
            self.issn_db_folder = (os.path.join(APPDIRS_DIRECTORY, ISSN_DB_NAME))
        elif os.path.isdir(CRL_FOLDER) and os.path.isfile(os.path.join(CRL_FOLDER, ISSN_DB_NAME)):
            self.issn_db_folder = CRL_FOLDER
            self.issn_db_folder = (os.path.join(CRL_FOLDER, ISSN_DB_NAME))     

    def add_about_file(self):
        """
        Add a basic about file to our data folder.
        """
        if not self.portable_install:
            about_file_location = os.path.join(self.marc_db_folder, 'about.txt')
            if not os.path.isfile(about_file_location):
                with open(about_file_location, 'w') as fout:
                    fout.write('This folder contains data files for utilities from the Center for Research Libraries.')
                    fout.write('\n')

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

    def get_input_files(self):

        valid_file_extensions = {'mrk', 'txt', 'tsv', 'csv', 'xlsx'}

        all_input_files = os.listdir(VALIDATOR_INPUT_FOLDER)
        for input_file in all_input_files:
            if input_file.startswith('~'):
                continue
            file_extension = input_file.split('.')[-1]
            if not file_extension.lower() in valid_file_extensions:
                continue
            self.input_files.append(input_file)


def print_validator_file_locations():
    from termcolor import colored, cprint
    import colorama
    
    file_locations = ValidatorFileLocations()

    colorama.init()

    name_color = 'cyan'
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
    not_installed = colored('not installed', not_installed_color, 'on_white')

    print('The {} is located at: '.format(main_data_folder), end='')
    cprint(file_locations.data_storage_folder, location_color)
    print('The {} is located at: '.format(local_marc_database), end='')
    cprint(file_locations.marc_db_location, location_color)
    if file_locations.issn_db_location:
        print('The {} is located at: '.format(issn_database), end='')
        cprint(file_locations.issn_db_location, location_color)
    else:
        print('The {} is {}.'.format(issn_database, not_installed))
