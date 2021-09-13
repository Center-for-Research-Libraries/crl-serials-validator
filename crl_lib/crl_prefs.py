"""
Read and write to a preference file called "config.ini".

This file will mainly be used for API keys, but could in theory contain almost
anything that can be expressed in key-value pairs.
"""
import os
import platform
import string
from appdirs import AppDirs


from crl_lib.preferences import Preferences
from crl_lib.api_keys import OclcApiKeys


class CrlFileLocations:
    """
    Base class. Find all relevant CRL database and data files.

    Set the class variable data_folder_path to set a default location for the data folder.
    """

    def __init__(self, data_folder_path=None):
        """
        Find/create "CRL MARC Machine" folder in home directory.
        Most data will be stored there.
        """
        self.appdirs = AppDirs(appname='CrlData', appauthor='CRL')

        self.home_folder = os.path.expanduser("~")
        if self.home_folder.startswith('H:'):
            # work around CRL home sometimes being set to H drive
            self.home_folder = os.path.join('C:\\Users', self.username)
        if platform.system() == 'Linux':
            self.check_for_wsl_on_windows()
        if data_folder_path:
            self.data_folder = self.data_folder_path
        else:
            self.data_folder = self.appdirs.user_data_dir
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
        

class CrlPreferences(Preferences):
    """
    A convenience class for Preferences using default CRL data.

    """
    def __init__(self):
        crl_file_locations = CrlFileLocations()
        super().__init__(data_folder=crl_file_locations.data_folder)


class CrlApiKeys(OclcApiKeys):
    """
    Convenience class for OclcApiKeys using CRL file locations.
    """

    def __init__(self, name_for_key=None):
        crl_file_locations = CrlFileLocations()
        super().__init__(data_folder=crl_file_locations.data_folder, name_for_key=name_for_key)
