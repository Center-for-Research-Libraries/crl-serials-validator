import os
import sys
from termcolor import colored, cprint

from crl_lib.api_keys import OclcApiKeys


IS_SEARCH_API_VALUE = colored('Se', 'green')
IS_METADATA_API_VALUE = colored('Md', 'cyan')
IS_DEFAULT_VALUE = colored('D', 'white', 'on_blue')


def print_terminal_page_header(header_str: str, header_color: str = 'green') -> None:
    header_bar = ''.join(['~' for _ in header_str])
    cprint(header_bar, header_color)
    cprint(header_str, header_color)
    cprint(header_bar, header_color)
    print('')


class ApiKeySetter:
    """
    Class to read and write API keys from/to the config file. This is mainly a
    GUI front end for the OclcApiKeys library.
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
        first_col = f'{colored(number_column, "yellow").ljust(2)}  {is_default_print.ljust(2)}'
        print('{}\t{}\t{}\t{}\t{}'.format(
            first_col,
            name.ljust(12),
            api_key.ljust(80),
            api_secret.ljust(25),
            for_which_apis_print,
            ))
        if header_row is True:
            for _ in range(0, 160):
                print('-', end='')
            print('')

    def make_which_apis_print_string(self, name: str) -> str:
        if name not in self.api_keys.api_keys:
            return ''
        return_string_list = []
        try:
            if self.api_keys.api_keys[name]['SEARCH'] == '1':
                return_string_list.append(IS_SEARCH_API_VALUE)
        except KeyError:
            self.api_keys.api_keys[name]['SEARCH'] = ''
        try:
            if self.api_keys.api_keys[name]['METADATA'] == '1':
                return_string_list.append(IS_METADATA_API_VALUE)
        except KeyError:
            self.api_keys.api_keys[name]['METADATA'] = ''
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
                    is_default_print = IS_DEFAULT_VALUE
                else:
                    is_default_print = ''

                which_apis_print = self.make_which_apis_print_string(name)

                self.print_row_to_terminal(str(i), name, api_key, api_secret, which_apis_print, is_default_print)

            print('')
            print('{}. Add a new key.'.format(colored('a', 'yellow')))
            print('{}. Remove a key.'.format(colored('r', 'yellow')))
            print('{}. Set a new default key.'.format(colored('d', 'yellow')))
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
        new_is_search = input('Key works with Search API? ({}/{}) '.format(colored('y', 'yellow'), colored('n', 'yellow')))
        new_is_metadata = input('Key works with Metadata API? ({}/{}) '.format(colored('y', 'yellow'), colored('n', 'yellow')))
        if not new_name:
            print('No name given; key not added.')
        elif not new_key:
            print('No key input; nothing added.')
        elif new_is_metadata and not new_secret:
            print('Metadata key must have API key secret; key not added.')

            new_is_default = '1' if new_is_default.lower().startswith('y') else ''
            new_is_search = '1' if new_is_search.lower().startswith('y') else ''
            new_is_metadata = '1' if new_is_metadata.lower().startswith('y') else ''

            self.api_keys.add_api_key(new_name, new_key, new_secret, new_is_search, new_is_metadata, new_is_default)

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


if __name__ == "__main__":
    a = ApiKeySetter()
