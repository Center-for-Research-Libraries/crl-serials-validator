import os
import sys
from tkinter import HORIZONTAL
from unicodedata import name
from termcolor import colored, cprint

from crl_lib.api_keys import OclcApiKeys
from crl_lib.wc_api_utilities import test_search_api, test_metadata_api


IS_SEARCH_API_KEY_VALUE = colored('Search', 'green')
IS_METADATA_API_KEY_VALUE = colored('Metadata', 'cyan')
IS_DEFAULT_KEY_VALUE = '  ' + colored('default', 'white', 'on_blue') + '  '
IS_NOT_DEFAULT_KEY_VALUE = '           '

SUCCESS_LINE = 'Key ' + colored('works', 'yellow') + ' with {} API.'
FAILURE_LINE = 'Key ' + colored('does not work', 'red') + ' with {} API.'
NOT_SET_LINE = FAILURE_LINE + ' ' + colored('{} not set.', 'red')

HORIZONTAL_LINE = ''.join(['-' for i in range(0, 109)])


def print_terminal_page_header(header_str: str, header_color: str = 'green') -> None:
    header_bar = ''.join(['~' for _ in header_str])
    cprint(header_bar, header_color)
    cprint(header_str, header_color)
    cprint(header_bar, header_color)
    print('')


class ApiKeySetter:
    """
    Class to read and write API keys from/to the config file. 
    
    This serves as a GUI front end for the OclcApiKeys library.
    """

    def __init__(self) -> None:
        self.api_keys = None
        self.names = []
        self.make_gui()

    @staticmethod
    def print_row_to_terminal(
            number_column: str, 
            name: str, 
            api_key: str, 
            api_secret: str, 
            for_which_apis_print: str, 
            is_default_print: str, 
            header_row: bool = False
        ) -> None:

        if header_row is True:
            print(HORIZONTAL_LINE)
            return

        first_col = f'{colored(number_column, "yellow").ljust(3)}{is_default_print}'

        print(f'{first_col}{name.ljust(12)}{colored("Key", "yellow")}: {api_key}')
        print(f'                        {colored("Secret", "yellow")}: {api_secret}')
        print(f'                        {colored("APIs", "yellow")}: {for_which_apis_print}')

        print(HORIZONTAL_LINE)

    def check_if_key_works_with_search_api(self, api_key: str) -> str:
        if api_key and test_search_api(api_key) is True:
            print(SUCCESS_LINE.format('Search'))
            return '1'

        if not api_key:
            print(NOT_SET_LINE.format('Search', 'API key'))
        else:
            print(FAILURE_LINE.format('Search'))
        return ''

    def check_if_key_works_with_metadata_api(self, api_key: str, api_secret: str) -> str:
        if api_key and api_secret and test_metadata_api(api_key, api_secret) is True:
            print(SUCCESS_LINE.format('Metadata'))
            return '1'
        if not api_key:
            print(NOT_SET_LINE.format('Metadata', 'API key'))
        elif not api_secret:
            print(NOT_SET_LINE.format('Metadata', 'API secret'))
        else:
            print(FAILURE_LINE.format('Metadata'))
        return ''

    def make_which_apis_work_with_key_print_string(self, name: str, api_key: str, api_secret) -> str:
        return_string_list = []
        if self.api_keys.api_keys[name]['SEARCH']:
            return_string_list.append(IS_SEARCH_API_KEY_VALUE)
        if self.api_keys.api_keys[name]['METADATA']:
            return_string_list.append(IS_METADATA_API_KEY_VALUE)
        return ', '.join(return_string_list)

    def make_gui(self) -> None:

        while True:
            self.api_keys = OclcApiKeys()

            os.system('cls' if os.name == 'nt' else 'clear')

            print_terminal_page_header('Set API Keys')

            self.names = list(self.api_keys.api_keys.keys())
            self.names.insert(0, '')

            self.print_row_to_terminal(' ', 'Name', 'API Key', 'API Secret', 'APIs', '', header_row=True)

            for i in range(1, len(self.names)):
                name = self.names[i]
                if not name:
                    continue
                api_key = self.api_keys.api_keys[name]['KEY']
                api_secret = self.api_keys.api_keys[name]['SECRET']

                if self.api_keys.api_keys[name]['DEFAULT'] == '1':
                    is_default_print = IS_DEFAULT_KEY_VALUE
                else:
                    is_default_print = IS_NOT_DEFAULT_KEY_VALUE

                which_apis_print = self.make_which_apis_work_with_key_print_string(name, api_key, api_secret)

                self.print_row_to_terminal(str(i), name, api_key, api_secret, which_apis_print, is_default_print)

            print('')
            print('{}. Add a new key.'.format(colored('a', 'yellow')))
            print('{}. Remove a key.'.format(colored('r', 'yellow')))
            print('{}. Set a new default key.'.format(colored('d', 'yellow')))
            print('{}. Test the keys.'.format(colored('t', 'yellow')))
            print('{}. Back to the main menu.'.format(colored('m', 'yellow')))
            print('{}. Quit the Validator.'.format(colored('q', 'yellow')))
            print('')
            choice_result = input('Your choice? ')

            if choice_result.lower() == 'a':
                self.add_key()

            elif choice_result.lower() == 'r':
                self.delete_key()

            elif choice_result.lower() == 'd':
                self.set_default_key()

            elif choice_result.lower() == 't':
                self.test_all_api_keys()

            elif choice_result.lower() == 'm':
                break
            elif choice_result.lower() == 'q':
                sys.exit()
            else:
                print("I didn't understand that.")
            print('')

    def add_key(self) -> None:
        new_name = input('{} name for key: '.format(colored('Enter', 'yellow')))
        new_key = input('{} API key: '.format(colored('Enter', 'yellow')))
        new_secret = input('{} API secret (if applicable): '.format(colored('Enter', 'yellow')))
        new_is_default = input('Make default key? ({}/{}) '.format(colored('y', 'yellow'), colored('n', 'yellow')))
        new_is_default = '1' if new_is_default.lower().startswith('y') else ''

        if not new_name:
            print('No name given; key not added.')
        elif not new_key:
            print('No key input; nothing added.')
        else:
            new_is_search = self.check_if_key_works_with_search_api(new_key)
            new_is_metadata = self.check_if_key_works_with_metadata_api(new_key, new_secret)
            self.api_keys.add_api_key(new_name, new_key, new_secret, new_is_search, new_is_metadata, new_is_default)
            input('Press Enter to continue.')

    def delete_key(self) -> None:
        to_delete = input('{} number to delete: '.format(colored('Enter', 'yellow')))
        try:
            name_to_delete = self.names[int(to_delete.strip())]
            try:
                self.api_keys.api_keys.pop(name_to_delete)
                self.api_keys.write_preferences_to_file()
            except IndexError:
                pass
        except (ValueError, TypeError, IndexError):
            print('Must enter a valid number to delete.')
            input('Press Enter to continue.')

    def set_default_key(self) -> None:
        new_default = input('{} number to set as default: '.format(colored('Enter', 'yellow')))
        try:
            default_name = self.names[int(new_default)]
            for name in self.api_keys.api_keys:
                self.api_keys.api_keys[name]['DEFAULT'] = ''
            self.api_keys.api_keys[default_name]['DEFAULT'] = '1'
            self.api_keys.write_preferences_to_file()
        except (ValueError, TypeError, IndexError):
            print('Must enter a number to set default key.')
            input('Press Enter to continue.')

    def test_all_api_keys(self) -> None:
        for name in self.api_keys.api_keys:
            cprint(f'Testing {name}...', 'white', 'on_blue')
            works_with_search = self.check_if_key_works_with_search_api(self.api_keys.api_keys[name]['KEY'])
            works_with_metadata = self.check_if_key_works_with_metadata_api(
                self.api_keys.api_keys[name]['KEY'], self.api_keys.api_keys[name]['SECRET'])
            self.api_keys.api_keys[name]['SEARCH'] = works_with_search
            self.api_keys.api_keys[name]['METADATA'] = works_with_metadata
        self.api_keys.write_preferences_to_file()
        input('Press Enter to continue.')

if __name__ == "__main__":
    a = ApiKeySetter()
