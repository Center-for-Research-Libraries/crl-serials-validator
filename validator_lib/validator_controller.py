import logging

from validator_lib.validator_logger import set_validator_logger
from validator_lib.utilities import get_input_files, initialize_folders
from crl_lib.api_key_setter import ApiKeySetter
from crl_lib.issn_db import IssnDb
from validator_lib.choose_input_file_fields import InputFieldsChooser
from validator_lib.scan_input_files import InputFileScanner
from validator_lib.run_checks_process import ChecksRunner
from validator_lib.choose_disqualifying_issues import IssuesChooser


class ValidatorController:
    """
    Controller for the validation process, meant to be agnositc about a front end.
    """

    viable_input_formats = {'txt', 'xlsx', 'tsv', 'csv', 'mrk'}

    def __init__(self, log_to_screen=False, headless_mode=False):
        self.headless_mode = headless_mode
        self.log_to_screen = log_to_screen

        # Make sure the relevant folders exist.
        initialize_folders()

        self.input_files_seen = False
        self.marc_input_seen = False

        set_validator_logger(log_to_screen)

        logging.info('Beginning validation process.')

        self.check_input_folder()
        self.check_issn_db()
        
        if self.headless_mode is True:
            logging.info('Running in headless mode.')
            self.run_headless()

    def run_headless(self):
        self.download_api_data()
        self.run_checks_process()

    def check_issn_db(self):
        issn_db = IssnDb()
        if issn_db.conn is not None:
            logging.info('ISSN database is installed.')

    def check_input_folder(self):
        input_files = get_input_files()
        if not input_files:
            logging.warning('No input files found.')
        for input_file in input_files:
            logging.info('Saw input file {}'.format(input_file))
            for input_format in self.viable_input_formats:
                if input_file.lower().endswith(input_format):
                    self.input_files_seen = True
                    if input_format == 'mrk':
                        self.marc_input_seen = True

    def set_api_keys(self):
        self.print_popunder_window_warning()
        ApiKeySetter()
    
    def scan_input_files(self):
        InputFileScanner()

    def choose_input_fields(self):
        self.print_popunder_window_warning()
        InputFieldsChooser()

    def set_disqualifying_issues(self):
        self.print_popunder_window_warning()
        IssuesChooser()
    
    def run_checks_process(self):
        ChecksRunner()

    def print_popunder_window_warning(self):
        """
        When printing to screen, print a warning about potential popunders when setting API keys, wanted fields, or 
        disqualifying issues. If a GUI or web frontend is added to the project then this function can probably be 
        removed.
        """
        if self.log_to_screen is True:
            print('========================================================')
            print("Opening a new program window.")
            print("If you don't see it, please look for it in your taskbar.")
            print('========================================================')
