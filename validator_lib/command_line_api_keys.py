from collections import OrderedDict
import os

from validator_lib.validator_file_locations import ValidatorFileLocations
from crl_lib.api_keys import OclcApiKeys


class CommandLineApiKeys:
    """
    Set API keys for a headless/bulk processing install.
    """
    def __init__(self):
        self.file_locations = ValidatorFileLocations()

        self.api_keys = OclcApiKeys(self.file_locations.data_storage_folder)

        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print('')
            print('1 Show existing API keys.')
            print('2 Enter a new API key.')
            print('3 Delete an API key.')
            print('4 Choose a default API key.')
            print('Type "q" to quit.')
            print('')
            another = input('Your choice?\n')
            if another.startswith('1'):
                self.display_known_keys()
            elif another.startswith('2'):
                self.enter_new_key()
            elif another.startswith('3'):
                self.delete_key()
            elif another.startswith('4'):
                self.set_default_key()
            elif another.lower().startswith('q'):
                self.api_keys.write_preferences_to_file()
                break
            else:
                print("I didn't understand that.")

    def display_known_keys(self):
        default_name = self.api_keys.api_key_name
        print('Known API keys:')
        print('{:10}\t{:10}\t{}'.format('name', 'default', 'key'))
        for api_key_name in self.api_keys.api_keys:
            if api_key_name == default_name:
                is_default = '   *   '
            else:
                is_default = '       '
            print('{:10}\t{:10}\t{}'.format(api_key_name, is_default, self.api_keys.api_keys[api_key_name]))
        input('\nHit enter to continue.')

    def enter_new_key(self):
        name = input('Enter name: ')
        name = name.rstrip()
        if not name:
            print('No name entered. Skipping.')
            input('\nHit enter to continue.')
            return
        api_key = input('Enter key: ')
        api_key = api_key.rstrip()
        if not api_key:
            print('No API key entered. Skipping.')
            input('\nHit enter to continue.')
            return
        print('Entered name {}'.format(name))
        print('Entered key {}'.format(api_key))
        is_ok = input('OK?')
        if not is_ok.lower().startswith('y'):
            print('Skipped.')
            input('\nHit enter to continue.')
        else:
            print('Saved.')
            self.api_keys.config['API KEYS'][name] = api_key
            self.api_keys.write_preferences_to_file()
            self.api_keys.get_all_api_keys()
            input('\nHit enter to continue.')            

    def delete_key(self):
        key_list = self.get_api_keys_by_number()
        print('  \t{:10}\t{:10}'.format('name', 'api_key'))
        for i, api_key_tuple in enumerate(key_list):
            if i == 0:
                continue
            api_key_name = api_key_tuple[0]
            api_key = api_key_tuple[1]
            print('{}\t{:10}\t{:10}'.format(i, api_key_name, api_key))

        to_delete = input('Choose number of key to delete. Enter nothing to skip.\n')
        to_delete = to_delete.strip()
        try:
            to_delete = int(to_delete)
        except (TypeError, ValueError):
            pass
        if not to_delete or not isinstance(to_delete, int) or to_delete > i:
            print('Skipping.')
        else:
            delete_name = key_list[to_delete]
            print('Chose to delete number {}.'.format(to_delete))
            if delete_name:
                print('Will delete key attached to name {}.'.format(delete_name))
            is_ok = input('OK?\n')
            if not is_ok.lower().startswith('y'):
                print('Skipping.')
            else:
                print('Deleting.')
                del(self.api_keys.config['API KEYS'][delete_name])
                self.api_keys.write_preferences_to_file()
                del(self.api_keys)
                self.api_keys = OclcApiKeys(self.file_locations.data_storage_folder)

        input('\nHit enter to continue.') 

    def set_default_key(self):
        key_list = self.get_api_keys_by_number()
        print('  \t{:10}\t{:10}'.format('name', 'api_key'))
        for i, api_key_tuple in enumerate(key_list):
            if i == 0:
                continue
            api_key_name = api_key_tuple[0]
            api_key = api_key_tuple[1]
            print('{}\t{:10}\t{:10}'.format(i, api_key_name, api_key))    
        default_number = input('Choose default key.\n')
        try:
            default_name = key_list[int(default_number)][0]
            print('Setting {} as default name.'.format(default_name))
            self.api_keys.set_preferredapi_key_name(default_name)
            self.api_keys.write_preferences_to_file()
            del(self.api_keys)
            self.api_keys = OclcApiKeys(self.file_locations.data_storage_folder)
        except (ValueError, TypeError, IndexError):
            print('Skipping.')
        input('\nHit enter to continue.')


    def get_api_keys_by_number(self):
        key_list = ['']
        for api_key_name in self.api_keys.api_keys:            
            key_list.append((api_key_name, self.api_keys.api_keys[api_key_name]))
        return key_list
