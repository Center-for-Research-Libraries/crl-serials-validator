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


# Setting this to True will turn on debugging messages in the logging and automatically log to the screen
DEBUG_MODE = False


def set_validator_logger(log_to_screen):
    logger = logging.getLogger('validator')
    logger.setLevel(logging.DEBUG)
    log_directory = get_directory_location('logs')
    log_file_name = 'validator_log_{:%Y-%m-%d}.log'.format(datetime.datetime.now())
    log_file = os.path.join(log_directory, log_file_name)
    fh = logging.FileHandler(log_file)
    ch = logging.StreamHandler()
    
    if DEBUG_MODE is True:
        fh.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
    else:
        fh.setLevel(logging.INFO)
        ch.setLevel(logging.INFO)

    fh_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    ch_formatter = logging.Formatter('%(message)s')

    if log_to_screen is True:
        print('LOG TO SCREEN')
        ch.setFormatter(ch_formatter)
        logger.addHandler(ch)

    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)


class ValidatorController:
    """
    Controller for the validation process, meant to be agnositc about a front end.
    """

    viable_input_formats = {'txt', 'xlsx', 'tsv', 'csv', 'mrk'}

    def __init__(self, log_to_screen=False, headless_mode=False):
        self.headless_mode = headless_mode
        self.log_to_screen = log_to_screen

        # self.set_validator_logger()
        set_validator_logger(self.log_to_screen)
        self.logger = logging.getLogger('validator')

        self.logger.debug('DEBUGGUBG')

        if DEBUG_MODE is True:
            self.log_to_screen = True

        # Make sure the relevant folders exist.
        initialize_folders()

        self.input_files_seen = False
        self.marc_input_seen = False

        self.logger.info('Beginning validation process.')

        self.check_input_folder()
        self.check_issn_db()
        
        if self.headless_mode is True:
            self.logger.info('Running in headless mode.')
            self.run_headless()

    def run_headless(self):
        self.download_api_data()
        self.run_checks_process()

    def check_issn_db(self):
        issn_db = IssnDb(ignore_missing_db=True)
        if issn_db.found_issn_db is True:
            self.logger.info('ISSN database is installed.')

    def check_input_folder(self):
        input_files = get_input_files()
        if not input_files:
            self.logger.warning('No input files found.')
        for input_file in input_files:
            self.logger.info('Found input file {}'.format(input_file))
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
