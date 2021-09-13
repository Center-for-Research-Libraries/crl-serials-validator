import logging
import os
import datetime

from validator_lib.validator_file_locations import ValidatorFileLocations
from validator_lib.utilities import initialize_folders
from crl_lib.api_key_setter import ApiKeySetter
from validator_lib.choose_input_file_fields import InputFieldsChooser
from validator_lib.scan_input_files import InputFileScanner
from validator_lib.run_checks_process import ChecksRunner
from validator_lib.choose_disqualifying_issues import IssuesChooser


# Set the variable below to True to enable debug logging
DEBUG_MODE = False


class ValidatorController(ValidatorFileLocations):
    """
    Controller for the validation process, meant to be agnositc about a front end.
    """

    viable_input_formats = {'txt', 'xlsx', 'tsv', 'csv', 'mrk'}

    def __init__(self, headless_mode=False, log_level='info', portable_install=False):
        super().__init__(portable_install=False)

        self.headless_mode = headless_mode
        self.log_level = log_level
        self.debug_mode = DEBUG_MODE

        if self.headless_mode is True:
            self.log_level = 'warning'

        if DEBUG_MODE is True:
            self.log_level = 'debug'

        self.set_logging()

        self.log_file_location_results()

        # Make sure the relevant folders exist.
        initialize_folders()

        self.input_files_seen = False
        self.marc_input_seen = False

        self.check_input_folder()
        
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
        log_file = os.path.join(self.validator_logs_folder, log_file_name)
        logging.basicConfig(
            filename=log_file, 
            level=log_levels[self.log_level], 
            filemode='a', format='%(asctime)s\t%(message)s', datefmt="%Y-%m-%d %H:%M:%S")

    def check_input_folder(self):
        if not self.input_files:
            logging.warning('No input files found.')
        for input_file in self.input_files:
            logging.info('Found input file {}'.format(input_file))
            for input_format in self.viable_input_formats:
                if input_file.lower().endswith(input_format):
                    self.input_files_seen = True
                    if input_format == 'mrk':
                        self.marc_input_seen = True

    def set_api_keys(self):
        self.print_popunder_window_warning()
        ApiKeySetter(self.data_storage_folder)
    
    def scan_input_files(self):
        InputFileScanner(self.input_files)

    def choose_input_fields(self):
        self.print_popunder_window_warning()
        InputFieldsChooser(self.input_files)

    def set_disqualifying_issues(self):
        self.print_popunder_window_warning()
        IssuesChooser()
    
    def run_checks_process(self):
        ChecksRunner(
            self.data_storage_folder,
            self.validator_data_folder,
            self.input_files,
            self.validator_output_folder, 
            self.issn_db_location,
            running_headless=self.headless_mode)

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
