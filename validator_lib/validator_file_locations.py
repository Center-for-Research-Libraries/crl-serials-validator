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

        self.look_for_validator_data_folder()
        if not portable_install:
            self.look_for_crl_marc_machine_folder()
            self.look_for_crl_folder()

        if not self.data_storage_folder:
            self.data_storage_folder = self.validator_data_folder

        self.get_input_files()

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
        if not self.marc_db_location and not self.data_storage_folder and self.marc_db_name in dir_list:
            self.data_storage_folder = dir
            self.marc_db_location = os.path.join(dir, self.marc_db_name)

    def check_for_issn_db(self, dir, dir_list):
        if not self.issn_db_location and self.issn_db_name in dir_list:
            self.issn_db_location = os.path.join(dir, self.issn_db_name)
            if not self.data_storage_folder:
                self.data_storage_folder = dir

    def look_for_validator_data_folder(self):
        self.check_folder(self.validator_data_folder)

    def look_for_crl_marc_machine_folder(self):
        marc_machine_folder = os.path.join(self.home_folder, 'CRL MARC Machine')
        self.check_folder(marc_machine_folder)

    def look_for_crl_folder(self):
        crl_folder = os.path.join(self.home_folder, 'CRL')
        self.check_folder(crl_folder)

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
        dir_names = ['input', 'output', 'data', 'logs']
        validator_dir = os.getcwd()
        for dir_name in dir_names:
            dir = os.path.join(validator_dir, dir_name)
            if not os.path.isdir(dir):
                logging.info('Creating directory {}'.format(dir))
                os.mkdir(dir)
        if not os.path.isdir(self.crl_folder):
            os.mkdir(self.crl_folder)
        self.check_about_file()

    def check_about_file(self):
        about_file_location = os.path.join(self.crl_folder, 'about.txt')
        if not os.path.isfile(about_file_location):
            with open(about_file_location, 'w') as fout:
                fout.write('This folder contains data files for utilities from the Center for Research Libraries.\n')
