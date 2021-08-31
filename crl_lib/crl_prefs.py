"""
Read and write to a preference file called "config.ini".

This file will mainly be used for API keys, but could in theory contain almost
anything that can be expressed in key-value pairs.
"""
import os
import configparser
import random
import platform
import string


class CrlFileLocations:
    """
    Base class. Find all relevant CRL database and data files.

    Set the class variable data_folder_path to set a default location for the data folder.
    """

    data_folder_path = None

    def __init__(self):
        """
        Find/create "CRL MARC Machine" folder in home directory.
        Most data will be stored there.
        """
        self.home_folder = os.path.expanduser("~")
        if self.home_folder.startswith('H:'):
            # work around CRL home sometimes being set to H drive
            self.home_folder = os.path.join('C:\\Users', self.username)
        if platform.system() == 'Linux':
            self.check_for_wsl_on_windows()
        if self.data_folder_path:
            self.data_folder = self.data_folder_path
        else:
            self.data_folder = os.path.join(self.home_folder, "CRL MARC Machine")
        if not os.path.exists(self.data_folder):
            os.mkdir(self.data_folder)

        self.api_hits_db_file = os.path.join(self.data_folder, "api_hits.db")
        self.holders_api_db_file = os.path.join(self.data_folder, "holders_from_api.db")
        self.marc_collection_db_file_location = os.path.join(self.data_folder, "marc_collection.db")
        self.crl_catalog_file = os.path.join(self.data_folder, "crl_full_catalog.mrk")
        self.issn_db_file_location = self.find_issn_db()

    def check_for_wsl_on_windows(self):
        """
        With systems using WSL, we'll try to use the data folder in the Windows home directory. This method depends on
        the user having the same WSL and Windows usernames.

        Note that getpass doesn't work on Windows, which is why it's only imported if the system detects a Linux
        install.
        """
        import getpass
        username = getpass.getuser()
        windows_home_folder = os.path.join('/mnt/c/Users', username)

        if os.path.isdir(windows_home_folder):
            self.home_folder = windows_home_folder

    def find_issn_db(self):
        """
        On Nate's machine or another set up like it, the ISSN db will be in a set file in the data folders. On CRL 
        machines in the building the db will be in a specific folder in the Technical Services drive, which may be 
        mapped to one of many different letters.

        The network drives aren't mapped by default under Windows Subsystem for Linux, so I'm not including support for
        using it on a machine inside CRL. Such machines should still find a local copy of the database in the home 
        directory.
        """
        db_filename = 'ISSN_db.db'

        dbfile = os.path.join(self.data_folder, db_filename)
        if os.path.isfile(dbfile):
            return dbfile

        dropbox_data_folder = 'home/nflorin/work/Data_Files'
        dbfile = os.path.join(dropbox_data_folder, db_filename)
        if os.path.isfile(dbfile):
            return dbfile
        db_folder_name = "ISSN database"
        # find DB file on CRL Windows machine
        for letter in list(string.ascii_uppercase):
            drive = "{}:".format(letter)
            dbfile = os.path.join(drive, db_folder_name, db_filename)
            if os.path.isfile(dbfile):
                return dbfile
        # if that didn't work, try the general data folder
        dbfile = os.path.join(self.data_folder, db_filename)
        if os.path.isfile(dbfile):
            return dbfile
        

class CrlPreferences(CrlFileLocations):

    """
    Base class for reading the general preferences for these libraries.
    The class looks for a file called "config.ini".
    This should be in the "CRL MARC Machine" folder in the user's home directory.

    This class doesn't do much on its own outside of reading data and some
    general housekeeping, and is inteded for use as a base class for other
    classes relating to specific preferences.

    Usage:

        from crl_lib.crl_prefs import CrlPreferences
        p = CrlPreferences()

        # get config keys & values
        for section in p.config:
            for key in p.config[section]:
                value = p.config[section][value]

        # delete a key
        p.remove_preference_key(section, key)

        # add a key & value (or just change the value)
        p.update_preference_value(section, key, value)

        # adding a new section and a key & value pair
        p.update_preference_value(section, key, value, create_new_section=True)

        # write the preferences to the "config.ini" file
        p.write_preferences_to_file()

    """

    def __init__(self):
        super().__init__()
        # Get preferences file location. Create it if it doesn't exist.
        # Get the location of the local SQLite MARC database.
        self.preferences_file_name = os.path.join(self.data_folder, "config.ini")
        if not os.path.isfile(self.preferences_file_name):
            fout = open(self.preferences_file_name, "w", encoding="utf8")
            fout.close()

        # Read the contents of the "config.ini" file
        self.config = configparser.ConfigParser()
        self.config.read(self.preferences_file_name)

    def update_preference_value(self, section, key, value, create_new_section=False):
        """
        Change a value, or add a key-value pair
        """
        if section not in self.config:
            if not create_new_section:
                raise KeyError("Section {} not in config.".format(section))
            self.config[section] = {}
        self.config[section][key] = value

    def remove_preference_key(self, section, key):
        try:
            self.config[section].pop(key)
        except KeyError:
            pass

    def write_preferences_to_file(self):
        with open(self.preferences_file_name, "w", encoding="utf8") as fout:
            self.config.write(fout)


class CrlApiKeys(CrlPreferences):

    """
    Class for getting WorldCat Search API keys from a preferences file.

    Usage:

        k = CrlApiKeys()
        api_key =  k.api_key  # returns actual key
        k.api_key = 'nate'    # change API key based on actual name
        # new instance using arbitrary key name.
        k2 = CrlApiKeys('constance')

    """

    def __init__(self, name_for_key=None):
        super().__init__()
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
