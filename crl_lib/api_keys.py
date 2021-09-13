import random
import os

from crl_lib.preferences import Preferences


class OclcApiKeys(Preferences):

    """
    Class for getting WorldCat Search API keys from a preferences file.

    Usage:

        k = OclcApiKeys()
        api_key =  k.api_key  # returns actual key
        k.api_key = 'nate'    # change API key based on actual name
        # new instance using arbitrary key name.
        k2 = OclcApiKeys('constance')

    """

    def __init__(self, data_folder, name_for_key=None):
        
        if not os.path.isdir(data_folder):
            raise Exception('Invalid data folder sent to api_keys. Folder is {}'.format(data_folder))
        
        super().__init__(data_folder=data_folder, preferences_file_name='api_keys.ini')
        self.api_keys = {}
        self.get_all_api_keys()
        self.api_key_name = self.set_api_key_name(name_for_key)

    @property
    def api_key(self):
        try:
            return self.config["API KEYS"][self.api_key_name]
        except AttributeError:
            # no key set, probably because none in config.ini
            return None

    @api_key.setter
    def api_key(self, name_for_key=None):
        self.set_api_key_name(name_for_key)

    def get_api_key_name(self):
        return self.api_key_name

    def get_all_api_keys(self):
        try:
            for name in self.config['API KEYS'].keys():
                self.api_keys[name] = self.config['API KEYS'][name]
        except KeyError:
            # Add section, so that a segment will at least be added to config.ini
            self.config.add_section('API KEYS')

    def set_preferredapi_key_name(self, name):
        """
        Set the preferred API key name in the preferences. To make this permanent,
        the preferences file should be re-written at some point after this.
        """
        name = name.lower()
        try:
            self.config['API KEYS'][name]
        except KeyError:
            raise KeyError(
                "Can't use name {} as preferred API key; not in list of keys.".format(name))
        self.config['Preferred API Key'] = {name: '1'}

    def set_api_key_name(self, name_for_key=None):
        # No API keys read. THe user will have to add some, or the base script will have to deal with the issue
        if not self.config["API KEYS"]:
            self.api_key_name = None
            return

        if name_for_key:
            if name_for_key not in self.config["API KEYS"]:
                raise KeyError(
                    "Name {} not in API key list.".format(name_for_key))
            self.api_key_name = name_for_key
            return
        if "Preferred API Key" in self.config:
            preferred_name = None
            for name in self.config["Preferred API Key"]:
                if not preferred_name:
                    preferred_name = name
                else:
                    # Remove extra preferred names from the preferences.
                    # This is ultimately only meaningful in the prefs are then
                    # written back to the file.
                    self.remove_preference_key("Preferred API Key", name)
                if preferred_name:
                    return preferred_name
        # Fallback, choose a random name if none preferred.
        name = random.choice(list(self.api_keys.keys()))
        return name
