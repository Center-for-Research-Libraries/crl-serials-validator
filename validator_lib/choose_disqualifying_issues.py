"""
Class to allow the user to decide that some issues with the input data will be noted but will not cause the title to
fail checks.
"""

import webbrowser
from pprint import pprint
from termcolor import colored, cprint
import os
import sys

from validator_lib.validator_data import ERROR_GLOSSARY_URL
from validator_lib.validator_config import ValidatorConfig
from validator_lib.terminal_gui_utilities import print_terminal_page_header


class IssuesChooser:

    # Issue categories that should be at the top of sections.
    break_categories = {
        'binding_words_in_holdings', 'duplicate_holdings_id', 'holdings_out_of_range', 'title_in_jstor', 
        'invalid_local_issn', 'oclc_mismatch', 'line_583_error' }

    title_text = 'Select Disqualifying Issues'

    def __init__(self, issn_db_missing=False):
        super().__init__()

        self.issn_db_missing = issn_db_missing
        self.validator_config = ValidatorConfig()

        self.warnings = []
        self.int_vars = {}

        self.make_gui()

    def make_gui(self):
        yes_symbol = colored('yes', 'white', 'on_blue')
        no_symbol = colored('no', 'white', 'on_red')
        disabled_symbol = colored('n/a', 'magenta')

        while True:
            os.system('cls' if os.name == 'nt' else 'clear')

            column = 0
            issue_no = 0

            print_terminal_page_header('Select Disqualifying Issues')

            for issue in self.validator_config.issue_categories:
                issue_no += 1

                if issue in self.break_categories:
                    print('')
                    column = 0
                if column %2 == 0:
                    line_end = '\t\t'
                else:
                    line_end = '\n'
                column += 1

                number_color = 'yellow'
                if 'issn_db' in issue and self.issn_db_missing is True:
                    print_symbol = disabled_symbol
                    number_color = 'red'
                    # self.int_vars[issue].set(0)
                elif self.validator_config.config['disqualifying_issues'][issue] is True:
                    print_symbol = yes_symbol
                else:
                    print_symbol = no_symbol

                print('{}{}\t{}'.format(
                    colored(str(issue_no).ljust(4), 
                    number_color), issue.ljust(35), 
                    print_symbol.ljust(4)), end=line_end)

            print('')
            print('')
            print('{} to toggle the option between yes and no.'.format(colored('enter a number', 'yellow')))
            print('{}. Reset all values to the defaults.'.format(colored('d', 'yellow')))
            print('{}. Visit the Validator issues glossary in a web browser.'.format(colored('g', 'yellow')))
            print('{}. Return to the main menu.'.format(colored('m', 'yellow')))
            print('{}. Quit the Validator.'.format(colored('q', 'yellow')))

            user_choice = input(colored('Your choice: ', 'cyan'))

            if user_choice.lower().startswith('g'):
                self.open_glossary_on_wiki()
            elif user_choice.lower().startswith('d'):
                self.reset_fields()
            elif user_choice.lower().startswith('m'):
                break
            elif user_choice.lower().startswith('q'):
                sys.exit()
            elif user_choice.isdigit() and int(user_choice) >= 1 and int(user_choice) <= issue_no:
                issue = self.validator_config.issue_categories[int(user_choice) - 1]
                if  self.validator_config.config['disqualifying_issues'][issue] is True:
                     self.validator_config.config['disqualifying_issues'][issue] = False
                else:
                     self.validator_config.config['disqualifying_issues'][issue] = True
                self.validator_config.write_validator_config_file()

    def open_glossary_on_wiki(self):
        webbrowser.open(ERROR_GLOSSARY_URL)

    def ok_clicked(self):
        for issue in self.validator_config.config['disqualifying_issues']:
            issue_state = self.int_vars[issue].get()
            self.validator_config.config['disqualifying_issues'][issue] = bool(issue_state)
        self.validator_config.write_validator_config_file()
        self.cancelled()

    def cancelled(self):
        """Close without making any changes."""
        self.destroy()

    def reset_fields(self):
        disqualifying_issues = self.validator_config.get_default_disqualifying_issues()
        # YAML can't write OrderedDict, so convert to regular dict
        self.validator_config.config['disqualifying_issues'] = dict(disqualifying_issues)
        self.validator_config.write_validator_config_file()
        self.__init__(self.issn_db_missing)

    def get_default_disqualifying_issues():
        disqualifying_issues = OrderedDict({
            'bib_lvl_not_serial': True,
            'form_not_print': True,
            'record_type_not_language_material': True,
            'serial_type_not_periodical': True,
            'invalid_carrier_type': True,
            'invalid_media_type': True,
            'issn_db_form_not_print': True,
            'issn_db_serial_type_not_periodical': True,
            'no_oclc_number': True,
            'no_worldcat_record': True,

            'binding_words_in_holdings': True,
            'completeness_words_in_holdings': True,
            'nonprint_words_in_holdings': True,

            'title_in_jstor': False,

            'duplicate_holdings_id': True,
            'duplicate_local_oclc': True,
            'duplicate_wc_oclc': True,

            'holdings_out_of_range': True,
            'holdings_out_of_issn_db_date_range': True,

            'invalid_local_issn': True,
            'issn_mismatch': True,
            'local_issn_does_not_match_wc_issn_a': False,
            'local_issn_does_not_match_issn_db': False,

            'oclc_mismatch': True,
            'title_mismatch': True,

            'line_583_error': True,
            'marc_validation_error': True,
            'missing_field_852a': True,
        })
        return disqualifying_issues


if __name__ == "__main__":
    IssuesChooser()
