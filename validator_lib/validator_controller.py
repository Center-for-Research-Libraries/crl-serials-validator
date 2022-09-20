import logging
import os
import datetime
import webbrowser
import sys
import gc
from termcolor import cprint

from validator_lib.validator_data import (
    CRL_FOLDER, ISSN_DB_LOCATION, MARC_DB_LOCATION, DOCS_URL, 
    VALIDATOR_INPUT_FOLDER, VALIDATOR_DATA_FOLDER, 
    VALIDATOR_OUTPUT_FOLDER, LOG_FILE_LOCATION)
from validator_lib.choose_input_file_fields import InputFieldsChooser
from validator_lib.scan_input_files import InputFileScanner
from validator_lib.run_checks_process import ChecksRunner
from validator_lib.choose_disqualifying_issues import IssuesChooser
from validator_lib.validator_config import ValidatorConfig

from crl_lib.api_key_setter import ApiKeySetter
from crl_lib.api_keys import OclcApiKeys


# Set the variable below to True to force debug logging
DEBUG_MODE = False

# List of input file extensions the process can currently handle
VIABLE_INPUT_FORMATS = {'txt', 'xlsx', 'tsv', 'csv', 'mrk'}


class ValidatorController:
    """
    Controller for the validation process, meant to be agnostic about the front 
    end.
    """

    def __init__(self, headless_mode=False, papr_output=False):

        super().__init__()

        self.headless_mode = headless_mode
        self.papr_output = papr_output

        self.set_logging()
        self.log_file_location_results()

        self.input_files_seen = False
        self.marc_input_seen = False

        self.input_files = []
        self.get_input_files()

        self.check_input_folder()
        
        if self.headless_mode is True and DEBUG_MODE is False:
            # self.log_to_screen = False
            logging.info('Running in headless mode.')

    def set_logging(self):
        """
        Initialize logging for the process.
        """
        if DEBUG_MODE is True:
            log_level = logging.DEBUG
        elif self.headless_mode is True:
            log_level = logging.WARNING
        else:
            log_level = logging.INFO

        logging.basicConfig(
            filename=LOG_FILE_LOCATION, 
            level=log_level, 
            filemode='a', 
            format='%(asctime)s\t%(message)s', datefmt="%Y-%m-%d %H:%M:%S")

    def print_break_line(self, line_before=False, line_length=120):
        if line_before is True:
            print('')
        break_line = ''
        for _ in range(0, line_length):
            break_line += '~'
        cprint(break_line, 'yellow')

    def get_input_files(self):
        all_input_files = os.listdir(VALIDATOR_INPUT_FOLDER)
        for input_file in all_input_files:
            if input_file.startswith('~'):
                continue
            file_extension = input_file.split('.')[-1]
            if not file_extension.lower() in VIABLE_INPUT_FORMATS:
                continue
            self.input_files.append(input_file)

    def check_input_folder(self):
        if not self.input_files:
            logging.warning('No input files found.')
        for input_file in self.input_files:
            logging.info('Found input file {}'.format(input_file))
            for input_format in VIABLE_INPUT_FORMATS:
                if input_file.lower().endswith(input_format):
                    self.input_files_seen = True
                    if input_format == 'mrk':
                        self.marc_input_seen = True

    def open_project_docs(self):
        webbrowser.open(DOCS_URL)

    def set_api_keys(self):
        self.print_break_line()
        api_setter_obj = ApiKeySetter()
        del api_setter_obj.api_keys
        gc.collect()
        self.print_break_line(line_before=True)

    def scan_input_files(self):
        input_file_scanner = InputFileScanner(self.input_files)
        input_file_scanner.scan_input_files()

    def choose_input_fields(self):
        InputFieldsChooser(self.input_files)

    def set_disqualifying_issues(self):
        IssuesChooser()

    def run_checks_process(self):
        error_message, warning_messages = self.check_if_run_is_possible()
        for warning_message in warning_messages:
            logging.warning(warning_message)
        if error_message:
            logging.error(error_message)
            sys.exit()

        self.clear_output_folder()
        x = 0
        for input_file in self.input_files:
            x += 1
            validator_config_object = ValidatorConfig()

            input_fields = validator_config_object.get_input_fields(input_file)       
            disqualifying_issue_categories = validator_config_object.get_disqualifying_issue_categories(input_file)

            if not input_fields:
                warning_message = 'No input fields set for file {}. Skipping.'.format(input_file)
                logging.warning(warning_message)
                continue
            del(validator_config_object)

            ChecksRunner(
                input_file,
                input_fields,
                disqualifying_issue_categories,
                running_headless=self.headless_mode,
                papr_output=self.papr_output)

    def log_file_location_results(self):
        if os.path.isfile(MARC_DB_LOCATION):
            logging.info('Found MARC database at {}'.format(MARC_DB_LOCATION))
        else:
            logging.info('MARC database not found.')
        if ISSN_DB_LOCATION:
            logging.info('Found ISSN database at {}'.format(ISSN_DB_LOCATION))
        else:
            logging.info('ISSN database not found.')

    def check_if_run_is_possible(self):
        """
        Make sure that everything is in place to actually complete a run. This 
        is a simple check, at the moment checking only if:
            1. An API key is set
        """

        warning_messages = []

        api_keys = OclcApiKeys(api_key_config_file_location=CRL_FOLDER)
        if not api_keys.api_key:
            logging.error('No WorldCat Search API key set.')
            error_message = "Please set a WorldCat Search API key."
            return error_message, warning_messages
        del(api_keys)

        return '', warning_messages

    def clear_output_folder(self):
        if self.headless_mode is not True:
            cprint(
                '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~',
                'cyan')
            while True:
                cprint(
                    'Should we erase all files in the output folder? (y/n)',
                    'cyan')
                clear_question = input()
                if clear_question.lower().startswith('n'):
                    return
                elif clear_question.lower().startswith('y'):
                    break
                else:
                    cprint("I didn't understand that.", 'red')
                    print('')
        output_files = os.listdir(VALIDATOR_OUTPUT_FOLDER)
        for output_file in output_files:
            logging.info(
                'Clearing output folder; deleting {}'.format(output_file))
            output_file_loc = os.path.join(VALIDATOR_OUTPUT_FOLDER, output_file)
            if not os.path.isfile(output_file_loc):
                continue
            try:
                os.remove(output_file_loc)
            except PermissionError:
                logging.warning(
                    "Could not delete file {} due to permissions error".format(
                        output_file))
        os.system('cls' if os.name == 'nt' else 'clear')
