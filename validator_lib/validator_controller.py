import logging
import os
import datetime

from validator_lib.utilities import get_input_files, initialize_folders, get_directory_location
from crl_lib.api_key_setter import ApiKeySetter
from crl_lib.issn_db import IssnDb
from validator_lib.choose_input_file_fields import InputFieldsChooser
from validator_lib.scan_input_files import InputFileScanner
from validator_lib.run_checks_process import ChecksRunner
from validator_lib.choose_disqualifying_issues import IssuesChooser


# Set the variable below to True to enable debug logging
DEBUG_MODE = False


class ValidatorController:
    """
    Controller for the validation process, meant to be agnositc about a front end.
    """

    viable_input_formats = {'txt', 'xlsx', 'tsv', 'csv', 'mrk'}
    data_directory = get_directory_location('data')
    logging_directory = get_directory_location('logs')

    def __init__(self, headless_mode=False, log_level='info'):
        self.headless_mode = headless_mode
        self.log_level = log_level
        self.debug_mode = DEBUG_MODE    

        if self.headless_mode is True:
            self.log_level = 'warning'

        if DEBUG_MODE is True:
            self.log_level = 'debug'

        self.set_logging()

        # Make sure the relevant folders exist.
        initialize_folders()

        self.input_files_seen = False
        self.marc_input_seen = False

        self.check_input_folder()
        self.check_issn_db()
        
        if self.headless_mode is True and DEBUG_MODE is False:
            self.log_to_screen = False
            logging.info('Running in headless mode.')

    def set_logging(self):
        """
        Initialize logging for the process.
        """
        log_levels = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR
        }

        log_file_name = 'validator_log_{:%Y-%m-%d}.log'.format(datetime.datetime.now())
        log_file = os.path.join(self.logging_directory, log_file_name)
        logging.basicConfig(
            filename=log_file, 
            level=log_levels[self.log_level], 
            filemode='a', format='%(asctime)s\t%(message)s', datefmt="%Y-%m-%d %H:%M:%S")


    def check_issn_db(self):
        issn_db_location = os.path.join(self.data_directory, 'ISSN_db.db')
        issn_db = IssnDb(issn_db_location=issn_db_location, ignore_missing_db=True)
        if issn_db.found_issn_db is True:
            logging.info('ISSN database is installed.')
        else:
            logging.info('ISSN database is not installed.')

    def check_input_folder(self):
        input_files = get_input_files()
        if not input_files:
            logging.warning('No input files found.')
        for input_file in input_files:
            logging.info('Found input file {}'.format(input_file))
            for input_format in self.viable_input_formats:
                if input_file.lower().endswith(input_format):
                    self.input_files_seen = True
                    if input_format == 'mrk':
                        self.marc_input_seen = True

    def set_api_keys(self):
        self.print_popunder_window_warning()
        ApiKeySetter(self.data_directory)
    
    def scan_input_files(self):
        InputFileScanner()

    def choose_input_fields(self):
        self.print_popunder_window_warning()
        InputFieldsChooser()

    def set_disqualifying_issues(self):
        self.print_popunder_window_warning()
        IssuesChooser()
    
    def run_checks_process(self):
        ChecksRunner(running_headless=self.headless_mode)

    def print_popunder_window_warning(self):
        """
        When printing to screen, print a warning about potential popunders when setting API keys, wanted fields, or 
        disqualifying issues. If a GUI or web frontend is added to the project then this function can probably be 
        removed.
        """
        print('========================================================')
        print("Opening a new program window.")
        print("If you don't see it, please look for it in your taskbar.")
        print('========================================================')
