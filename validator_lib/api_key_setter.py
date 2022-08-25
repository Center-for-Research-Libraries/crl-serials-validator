import os
import sys
from termcolor import colored, cprint
from collections import OrderedDict

from crl_lib.api_keys import OclcApiKeys


def print_terminal_page_header(header_str, header_color='green'):
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

    def __init__(self):
        self.api_keys = None
        self.names = []
        self.make_gui()

    @staticmethod
    def print_row_to_terminal(
            number_column, name, api_key, api_secret, is_default_print, header_row=False):
        print('{}\t{}\t{}\t{}'.format(
            colored(str(number_column),
                    'yellow').ljust(4),
            name.ljust(12),
            api_key.ljust(80),
            api_secret.ljust(20),
            is_default_print))
        if header_row is True:
            for _ in range(0, 150):
                print('-', end='')
            print('')

    def make_gui(self):

        while True:
            self.api_keys = OclcApiKeys()

            os.system('cls' if os.name == 'nt' else 'clear')

            print_terminal_page_header('Set API Keys')

            self.names = list(self.api_keys.api_keys.keys())
            self.names.insert(0, '')

            self.print_row_to_terminal(
                ' ', 'Name', 'API Key', 'API Secret', '', header_row=True)

            for i in range(1, len(names)):
                name = self.names[i]
                if not name:
                    continue
                is_default_print = ''
                api_key = self.api_keys.api_keys[name]['KEY']
                api_secret = self.api_keys.api_keys[name]['SECRET']
                if self.api_keys.api_keys[name]['DEFAULT'] == '1':
                    is_default_print = colored('default', 'white', 'on_blue')
                self.print_row_to_terminal(i, name, api_key, api_secret, is_default_print)

            print('')
            print('{}. Add a new key.'.format(colored('a', 'yellow')))
            print('{}. Edit a key.'.format(colored('e', 'yellow')))
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

    def add_key(self):
        new_name = input('{} name for key: '.format(colored('Enter', 'yellow')))
        new_key = input('{} API key: '.format(colored('Enter', 'yellow')))
        new_secret = input('{} API secret (if applicable): '.format(colored('Enter', 'yellow')))
        new_is_default = input('Make default key? ({}/{}) '.format(colored('y', 'yellow'), colored('n', 'yellow')))
        if not new_name:
            print('No name given; key not added.')
        elif not new_key:
            print('No key input; nothing added.')
        else:
            if new_is_default.lower().startswith('y'):
                make_default = '1'
            else:
                make_default = ''

            self.api_keys.api_keys[new_name] = {
                'KEY': new_key,
                'SECRET': new_secret,
                'DEFAULT': make_default
            }
            self.api_keys.write_preferences_to_file()

    def delete_key(self):
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

    def set_default_key(self):
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
    a = ApiKeySetter('')
