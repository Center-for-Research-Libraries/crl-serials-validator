import random
import os
import configparser
import yaml
import sys

from crl_lib.crl_file_locations import get_api_key_file_location


class OclcApiKeyError(Exception):
    """
    Generic error class for API key errors.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class OclcApiKeys:
    """
    Class for getting WorldCat Search API keys from a preferences file.

    Usage:

        k = OclcApiKeys()
        api_key =  k.api_key  # returns actual key
        k.api_key = 'nate'    # change API key based on actual name
        # new instance using arbitrary key name.
        k2 = OclcApiKeys('constance')

    """
    api_keys = {}
    api_key_config_file_location = None

    def __init__(self, name: str = '', api_key_config_file_location: str = '') -> None:

        if api_key_config_file_location and not api_key_config_file_location.endswith('yaml'):
            api_key_config_file_location = os.path.join(api_key_config_file_location, 'api_keys.yaml')

        self.name_for_key = name
        self.find_config_file(api_key_config_file_location)
        self.check_api_key_config_file_location()
        self.api_keys = {}

        self.api_key_name = ''
        self.config = ''

        self.read_config_file()

    def __del__(self) -> None:
        pass

    def reset_api_keys(self) -> None:
        """
        Set the YAML config dict to the default if no data exists
        """
        self.api_keys = {}

    def find_config_file(self, api_key_config_file_location: str) -> None:
        if not api_key_config_file_location:
            api_key_config_file_location = get_api_key_file_location()
        self.api_key_config_file_location = api_key_config_file_location

    def make_config_directory(self, my_dir) -> None:
        """
        Make the configuration directory if it doesn't exist.
        This function will recurse until it either fails or creates the directory.
        """
        if os.path.isdir(my_dir):
            return
        sub_dir = os.path.split(my_dir)[0]
        if sub_dir == my_dir:
            raise Exception("Can't make directory for configuration file.")
        if not os.path.isdir(sub_dir):
            self.make_config_directory(sub_dir)
        os.mkdir(my_dir)

    def check_api_key_config_file_location(self) -> None:
        if not os.path.isfile(self.api_key_config_file_location):
            old_file_location = self.api_key_config_file_location.replace('api_keys.yaml', 'api_keys.ini')
            print(old_file_location)
            if os.path.isfile(old_file_location):
                self.replace_old_config_file(old_file_location)
            config_dir = os.path.split(self.api_key_config_file_location)[0]
            self.make_config_directory(config_dir)
            if not os.path.isfile(self.api_key_config_file_location):
                self.reset_api_keys()
                self.write_preferences_to_file()

    def read_config_file(self) -> None:
        with open(self.api_key_config_file_location, 'r', encoding='utf8') as fin:
            self.api_keys = yaml.full_load(fin)

    def add_api_key(
        self, 
        name: str, 
        api_key: str, 
        api_secret: str, 
        is_search: str, 
        is_metadata: str,
        is_default: str
    ) -> None:
        self.alter_api_key(name, api_key, api_secret, is_search, is_metadata, is_default, True)

    def update_api_key(
        self, 
        name: str, 
        api_key: str, 
        api_secret: str, 
        is_search: str, 
        is_metadata: str,
        is_default: str
    ) -> None:
        self.alter_api_key(name, api_key, api_secret, is_search, is_metadata, is_default, False)

    def alter_api_key(
        self, 
        name: str, 
        api_key: str, 
        api_secret: str, 
        is_search: str, 
        is_metadata: str, 
        is_default: str,
        is_new_key: bool
    ) -> None:
        if not name:
            raise OclcApiKeyError('Need name for API key.')
        if not api_key:
            raise OclcApiKeyError(f'No key value provided for name {name}')
        if is_new_key is True and name in self.api_keys:
            raise OclcApiKeyError(f'Key with name {name} already in API keys preference file.')
        elif is_new_key is False and name not in self.api_keys:
            raise OclcApiKeyError(f'Key with name {name} not found in API keys preference file.')

        # standardize boolean entries on '1' or blank
        is_search = '1' if is_search else ''
        is_metadata = '1' if is_metadata else ''
        is_default = '1' if is_default else ''

        self.api_keys[name] = {
            'KEY': api_key,
            'SECRET': api_secret,
            'DEFAULT': is_default,
            'SEARCH': is_search,
            'METADATA': is_metadata,
        }
        self.write_preferences_to_file()

    @property
    def api_key(self) -> str:
        try:
            return self.api_keys['KEYS'][self.api_key_name]
        except AttributeError:
            # no key set, probably because none in api_keys.yaml
            return ''

    @api_key.setter
    def api_key(self, name_for_key: str = '') -> None:
        self.set_api_key_name(name_for_key)

    def get_api_key_name(self) -> str:
        return self.api_key_name

    def set_preferred_api_key_name(self, name: str) -> None:
        """
        Set the preferred API key name in the preferences. To make this permanent,
        the preferences file should be re-written at some point after this.
        """
        name = name.lower()
        try:
            self.api_keys[name]['DEFAULT'] = '1'
        except KeyError:
            raise KeyError(f"Can't use name {name} as preferred API key; not in list of keys.")

    def set_api_key_name(self, name_for_key: str = '') -> None:
        # No API keys read. The user will have to add some, or the base script will have to deal with the issue
        if not self.api_keys:
            raise KeyError(f"No API keys set?")
        self.api_key_name = ''
        if name_for_key:
            if name_for_key not in self.api_keys:
                raise KeyError(f"Name {name_for_key} not in API key list.")
            self.api_key_name = name_for_key
        else:
            for name in self.api_keys:
                if self.api_keys[name]['DEFAULT']:
                    if not self.api_key_name:
                        self.api_key_name = name
                    else:
                        self.api_keys[name]['DEFAULT'] = ''
        if not self.api_key_name:
            # Fallback, choose a random name if none preferred.
            self.api_key_name = random.choice(list(self.api_keys.keys()))

    def remove_name(self, name: str) -> None:
        try:
            self.api_keys.pop(name)
        except KeyError:
            pass

    def write_preferences_to_file(self) -> None:
        for name in self.api_keys:
            for cat in self.api_keys[name]:
                if self.api_keys[name][cat] is None:
                    self.api_keys[name][cat] = ''
        try:
            with open(self.api_key_config_file_location, "w", encoding="utf8") as fout:
                yaml.dump(self.api_keys, fout)
        except PermissionError:
            print('API config file could not be created due to PermissionError.')
            sys.exit(f'Location is {self.api_key_config_file_location}')

    def replace_old_config_file(self, old_file_location: str) -> None:
        """
        Read any old api_keys.ini files found and replace them with api_keys.yaml file.
        """
        yaml_dict = {}
        config = configparser.ConfigParser()
        config.read(old_file_location)
        print(old_file_location)
        for name in config['API KEYS']:
            print(name)
            yaml_dict[name] = {
                'KEY': config['API KEYS'][name],
                'SECRET': '',
                'DEFAULT': '',
                'METADATA': '',
                'SEARCH': '1'
            }
        try:
            for name in config['Preferred API Key']:
                yaml_dict[name]['DEFAULT'] = '1'
        except KeyError:
            pass
        print(yaml_dict)
        with open(self.api_key_config_file_location, 'w', encoding='utf8') as fout:
            yaml.dump(yaml_dict, fout)
