import os
import sys
from termcolor import colored, cprint
from collections import OrderedDict


from crl_lib.api_keys import OclcApiKeys
from crl_lib.terminal_gui_utilities import print_terminal_page_header


class ApiKeySetter:
    def __init__(self, data_folder):
        """
        data_folder should be the location (or desired location) of the API keys config file.
        """
        super().__init__()
        self.data_folder = data_folder
        self.make_gui()

    @staticmethod
    def print_row_to_terminal(number_column, name, api_key, is_default_print, header_row=False):
        print('{}\t{}\t{}\t{}'.format(
            colored(str(number_column), 'yellow').ljust(4), name.ljust(12), api_key.ljust(80), is_default_print))
        if header_row is True:
            for _ in range(0, 120):
                print('-', end='')
            print('')

    def make_gui(self):
        self.api_keys = OclcApiKeys(self.data_folder)
        
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')

            print_terminal_page_header('Set API Keys')

            self.get_names()
            self.print_row_to_terminal(' ', 'Name', 'API Key', '', header_row=True)

            i = 0
            for name in self.names_and_keys:
                if not name:
                    continue
                i += 1
                is_default_print = ''
                if name == self.default_key:
                    is_default_print = colored('default', 'white', 'on_blue')
                self.print_row_to_terminal(i, name, self.names_and_keys[name]['api_key'], is_default_print)

            print('')
            print('{}. Add a new key.'.format(colored('a', 'yellow')))
            print('{}. Remove a key.'.format(colored('r', 'yellow')))
            print('{}. Set a new default key.'.format(colored('d', 'yellow')))
            print('{}. Back to the main menu.'.format(colored('m', 'yellow')))
            print('{}. Quit the Validator.'.format(colored('q', 'yellow')))
            print('')
            choice_result = input('Your choice? ')

            if choice_result.lower() == 'a':
                new_name = input('{} name for key: '.format(colored('Enter', 'yellow')))
                new_key = input('{} API key: '.format(colored('Enter', 'yellow')))
                new_is_default = input('Make default key? ({}/{}) '.format(colored('y', 'yellow'), colored('n', 'yellow')))
                if not new_name:
                    print('No name given; key not added.')
                elif not new_key:
                    print('No key input; nothing added.')
                else:
                    if new_is_default.lower().startswith('y'):
                        make_default = True
                    else:
                        make_default = False
                    self.add_key(new_name, new_key, make_default)
                
            elif choice_result.lower() == 'r':
                to_delete = input('{} number to delete: '.format(colored('Enter', 'yellow')))
                try:
                    int(to_delete)
                    self.delete_key(to_delete)
                except (ValueError, TypeError):
                    print('Must enter a number to delete.')
                    input('Press Enter to continue.')
            elif choice_result.lower() == 'd':
                new_default = input('{} number to set as default: '.format(colored('Enter', 'yellow')))
                try:
                    int(new_default)
                    self.set_default_key(int(new_default))
                except (ValueError, TypeError):
                    print('Must enter a number to set default key.')
                    input('Press Enter to continue.')
            elif choice_result.lower() == 'm':
                break
            elif choice_result.lower() == 'q':
                sys.exit()
            else:
                print("I didn't understand that.")
            print('')

    def add_key(self, new_name, new_key, make_default):
        self.names_and_keys[new_name] = {'api_key': new_key}
        if make_default is True:
            self.default_key = new_name
        self.save_api_keys()

    def delete_key(self, number_to_delete):
        for name in self.names_and_keys:
            if int(number_to_delete) == self.names_and_keys[name]['number']:
                self.names_and_keys.pop(name)
                if self.default_key == 'name':
                    self.default_key = None
        self.save_api_keys()

    def set_default_key(self, number_as_default):
        for name in self.names_and_keys:
            if self.names_and_keys[name]['number'] == number_as_default:
                self.default_key = name
        self.save_api_keys()

    def get_names(self):
        self.api_keys.read_config_file()
        self.names_and_keys = OrderedDict()
        self.default_key = None
        self.api_keys.get_all_api_keys()
        number = 0
        for name in self.api_keys.config['API KEYS']:
            number += 1
            api_key = self.api_keys.api_keys[name]
            if self.api_keys.api_key_name == name:
                self.default_key = name
            self.names_and_keys[name] = {'api_key': api_key, 'number': number}

    def save_api_keys(self):
        """Look for API keys and default key set and save to config file."""
        self.api_keys.config['API KEYS'] = {}
        self.api_keys.config['Preferred API Key'] = {}
        for name in self.names_and_keys:
            if name and self.names_and_keys[name]['api_key']:
                self.api_keys.config['API KEYS'][name] = self.names_and_keys[name]['api_key']
                if name == self.default_key:
                    self.api_keys.config['Preferred API Key'] = {name: 1}
        self.api_keys.write_preferences_to_file()


if __name__ == "__main__":
    a = ApiKeySetter('')
