import logging
import os
import datetime
import webbrowser
import sys
import gc

from validator_lib.validator_file_locations import ValidatorFileLocations
from validator_lib.choose_input_file_fields import InputFieldsChooser
from validator_lib.scan_input_files import InputFileScanner
from validator_lib.run_checks_process import ChecksRunner
from validator_lib.choose_disqualifying_issues import IssuesChooser
from validator_lib.validator_config import ValidatorConfig
from validator_lib.api_key_setter import ApiKeySetter

from crl_lib.api_keys import OclcApiKeys

# Set the variable below to True to force debug logging
DEBUG_MODE = False


class ValidatorController(ValidatorFileLocations):
    """
    Controller for the validation process, meant to be agnositc about a front end.
    """

    viable_input_formats = {'txt', 'xlsx', 'tsv', 'csv', 'mrk'}
    docs_url = 'https://github.com/Center-for-Research-Libraries/validator/blob/main/README.md'

    def __init__(self, headless_mode=False, log_level='info', portable_install=False, single_file_run=False):
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
        self.initialize_folders()

        self.input_files_seen = False
        self.marc_input_seen = False

        self.check_input_folder()
        
        if self.headless_mode is True and DEBUG_MODE is False:
            # self.log_to_screen = False
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

    def open_project_docs(self):
        webbrowser.open(self.docs_url)

    def set_api_keys(self):
        self.print_popunder_window_warning()
        api_setter_obj = ApiKeySetter(self.data_storage_folder)
        del api_setter_obj.api_keys
        gc.collect()

    def scan_input_files(self):
        InputFileScanner(self.input_files)

    def choose_input_fields(self):
        self.print_popunder_window_warning()
        InputFieldsChooser(self.input_files)

    def set_disqualifying_issues(self):
        self.print_popunder_window_warning()
        if self.issn_db_location is None:
            IssuesChooser(issn_db_missing=True)
        else:
            IssuesChooser(issn_db_missing=False)

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
                self.data_storage_folder,
                self.validator_data_folder,
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


    def check_if_run_is_possible(self):
        """
        Make sure that everything is in place to actually complete a run. This is a simple check, at the moment checking only if:
            1. An API key is set
        """

        warning_messages = []

        api_keys = OclcApiKeys(self.data_storage_folder)
        if not api_keys.api_key:
            logging.error('No WorldCat Search API key set.')
            error_message = "Please set a WorldCat Search API key."
            return error_message, warning_messages
        del(api_keys)

        return '', warning_messages


    def clear_output_folder(self):
        if self.headless_mode is not True:
            while True:
                print('------------')
                print('Should we erase all files in the output folder? (Y/N)')
                clear_question = input()
                if clear_question.lower().startswith('n'):
                    return
                elif clear_question.lower().startswith('y'):
                    break
                else:
                    print("I didn't understand that.\n")
        output_files = os.listdir(self.validator_output_folder)
        for output_file in output_files:
            logging.info('Clearing output folder; deleting {}'.format(output_file))
            output_file_loc = os.path.join(self.validator_output_folder, output_file)
            if not os.path.isfile(output_file_loc):
                continue
            try:
                os.remove(output_file_loc)
            except PermissionError:
                logging.warning("Could not delete file {} due to permissions error".format(output_file))
