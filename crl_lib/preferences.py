import os
import configparser


class Preferences:

    """
    Base class for reading the general preferences for these libraries.
    The class looks for a file called "config.ini".

    This class doesn't do much on its own outside of reading data and some
    general housekeeping, and is inteded for use as a base class for other
    classes relating to specific preferences.

    Usage:

        from crl_lib.preferences import Preferences
        p = Preferences()

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

    def __init__(self, data_folder=None, preferences_file_name=None):
        if not preferences_file_name:
            preferences_file_name = 'config.ini'
        # Get preferences file location. Create it if it doesn't exist.
        self.preferences_file_location = os.path.join(data_folder, preferences_file_name)
        if not os.path.isfile(self.preferences_file_location):
            fout = open(self.preferences_file_location, "w", encoding="utf8")
            fout.close()

        # Read the contents of the "config.ini" file
        self.config = configparser.ConfigParser()
        self.config.read(self.preferences_file_location)

    def __del__(self):
        """
        Save the config file on crash or other unplanned close.
        """
        self.write_preferences_to_file()

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
        with open(self.preferences_file_location, "w", encoding="utf8") as fout:
            self.config.write(fout)
