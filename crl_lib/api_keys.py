import random
from pathlib import Path
import yaml
import sys
from typing import Dict, Union
from bookops_worldcat.authorize import WorldcatAccessToken
from bookops_worldcat.errors import WorldcatAuthorizationError

from crl_lib import CRL_FOLDER, check_for_crl_directory

API_KEY_CONFIG_FILE_PATH = Path.joinpath(CRL_FOLDER, "api_keys.yaml")


def check_key_on_search_api(api_key: str, api_key_secret: str) -> bool:
    """
    Checks if the provided API key and secret can successfully authenticate
    with the WorldCat Search API.

    Args:
        api_key (str): The API key to be tested.
        api_key_secret (str): The secret associated with the API key.

    Returns:
        bool: True if the API key and secret are valid and authentication
        is successful, False otherwise.
    """
    try:
        token = WorldcatAccessToken(api_key, api_key_secret, scopes="wcapi")
        return True
    except WorldcatAuthorizationError:
        return False


def check_key_on_metadata_api(api_key: str, api_key_secret: str) -> bool:
    """
    Checks if the provided API key and secret can successfully authenticate
    with the WorldCat Metadata API.

    Args:
        api_key (str): The API key to be tested.
        api_key_secret (str): The secret associated with the API key.

    Returns:
        bool: True if the API key and secret are valid and authentication
        is successful, False otherwise.
    """
    try:
        token = WorldcatAccessToken(
            api_key, api_key_secret, scopes="WorldCatMetadataAPI"
        )
        return True
    except WorldcatAuthorizationError:
        return False


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

    api_keys: Dict[str, Dict[str, str]] = {}

    def __init__(self, name_for_key: str = "") -> None:
        """
        Initializes an instance of the OclcApiKeys class.

        Args:
            name_for_key (str, optional): The name associated with the API key. Defaults to an empty string.

        The constructor sets up the initial state, creates the necessary directories
        if they don't exist, reads the configuration file to load API keys,
        and converts any existing configuration files. It also sets the API key
        name based on the provided or default name.
        """

        self.name_for_key = name_for_key
        self.api_keys = {}

        self.api_key_name = ""
        self.config = ""

        check_for_crl_directory()
        self.read_config_file()
        self.convert_config_file()

        self.set_api_key_name(self.name_for_key)

    def __del__(self) -> None:
        pass

    def read_config_file(self) -> None:
        """
        Reads the API key configuration file into memory.

        This function attempts to read the configuration file defined
        by the API_KEY_CONFIG_FILE_PATH variable.
        """
        try:
            with open(API_KEY_CONFIG_FILE_PATH, "r", encoding="utf8") as fin:
                self.api_keys = yaml.full_load(fin)
        except FileNotFoundError:
            pass

    def convert_config_file(self) -> None:
        """
        Converts "1" or "" in yaml to a boolean.

        This is for older installations where "1" was used in space of True.
        """
        changed = False
        keys_to_check = ["DEFAULT", "METADATA", "SEARCH"]
        for name in self.api_keys:
            for my_key in keys_to_check:
                if str(self.api_keys[name][my_key]) == "1":
                    self.api_keys[name][my_key] = True
                    changed = True
                if str(self.api_keys[name][my_key]) == "":
                    self.api_keys[name][my_key] = False
                    changed = True
        if changed:
            self.write_api_key_preferences_to_file()

    def check_all_keys_against_apis(self) -> None:
        """
        Checks all keys against the WorldCat Search and Metadata APIs.

        This function loops through all of the API keys and checks if they work
        with the WorldCat Search and Metadata APIs. If any of the keys were
        previously marked as working with an API but now don't, or previously
        marked as not working but now do, the preferences file is updated with
        the new values.

        Args:
            None

        Returns:
            None
        """

        changed = False
        for name in self.api_keys:
            search_ok = self.check_key_against_search_api(name)
            metadata_ok = self.check_key_against_metadata_api(name)
            if search_ok != self.api_keys[name]["SEARCH"]:
                self.api_keys[name]["SEARCH"] = search_ok
                changed = True
            if metadata_ok != self.api_keys[name]["METADATA"]:
                self.api_keys[name]["METADATA"] = metadata_ok
                changed = True
        if changed is True:
            self.write_api_key_preferences_to_file()

    def check_key_against_metadata_api(self, name: str) -> bool:
        """
        Checks the API key associated with the given name against the
        WorldCat Metadata API.

        Args:
            name (str): The name of the API key.

        Returns:
            bool: True if the API key works with the WorldCat Metadata API,
                False otherwise.
        """
        metadata_ok = check_key_on_metadata_api(
            self.api_keys[name]["KEY"], self.api_keys[name]["SECRET"]
        )
        return metadata_ok

    def check_key_against_search_api(self, name: str) -> bool:
        """
        Checks the API key associated with the given name against the
        WorldCat Search API.

        Args:
            name (str): The name of the API key.

        Returns:
            bool: True if the API key works with the WorldCat Search API,
                False otherwise.
        """
        search_ok = check_key_on_search_api(
            self.api_keys[name]["KEY"], self.api_keys[name]["SECRET"]
        )
        return search_ok

    def add_or_update_api_key(
        self,
        name: str,
        my_key: str,
        my_secret: str,
        is_search: bool,
        is_metadata: bool,
        is_default: bool,
        is_new_key: bool,
    ) -> None:
        """
        Add or update an API key in the preferences file.

        If the name for the new key is already in the file, it will be
        updated with the new information. If the name is not in the file,
        it will be added.

        Args:
            name (str): The name of the key.
            my_key (str): The key to add or update.
            my_secret (str): The secret to add or update.
            is_search (bool): Whether the key is valid for use with the
                WorldCat Search API.
            is_metadata (bool): Whether the key is valid for use with the
                WorldCat Metadata API.
            is_default (bool): Whether the key should be the default.
            is_new_key (bool): Whether the key is being added or updated.

        Raises:
            OclcApiKeyError: If the name is blank, or if the key or secret is
                blank, or if the key is being added but the name is already
                in the file, or if the key is being updated but the name is
                not in the file.

        Returns:
            None
        """
        if not name:
            raise OclcApiKeyError("Need name for API key.")
        if not my_key:
            raise OclcApiKeyError(f"No key provided for name {name}")
        if not my_secret:
            raise OclcApiKeyError(f"No secret provided for name {name}")

        if is_new_key is True:
            if name in self.api_keys:
                raise OclcApiKeyError(
                    f"Key with name {name} already in API keys preference file."
                )
        else:
            if name not in self.api_keys:
                raise OclcApiKeyError(
                    f"Key with name {name} not found in API keys preference file."
                )

        self.api_keys[name] = {
            "KEY": my_key,
            "SECRET": my_secret,
            "DEFAULT": is_default,
            "SEARCH": is_search,
            "METADATA": is_metadata,
        }
        self.write_api_key_preferences_to_file()

    @property
    def api_key(self) -> str:
        """
        The currently selected API key.

        Returns:
            str: The currently selected API key. If no key is selected, returns
                an empty string.
        """

        try:
            return self.api_keys[self.api_key_name]["KEY"]
        except AttributeError:
            # no key set, probably because none in api_keys.yaml
            return ""

    @api_key.setter
    def api_key(self, name_for_key: str = "") -> None:
        """
        Set the currently selected API key by name.

        If no name is given, the value of `api_key_name` is used.

        Args:
            name_for_key (str, optional): The name of the API key to select. Defaults to "".
        """

        self.set_api_key_name(name_for_key)

    @property
    def api_key_secret(self) -> str:
        """
        The secret associated with the currently selected API key.

        Returns:
            str: The secret associated with the currently selected API key. If no key is selected, returns
                an empty string.
        """
        try:
            return self.api_keys[self.api_key_name]["SECRET"]
        except AttributeError:
            # no key set, probably because none in api_keys.yaml
            return ""

    @api_key_secret.setter
    def api_key_secret(self, name_for_key: str = "") -> None:
        """
        Set the currently selected API key secret by name.

        If no name is given, the value of `api_key_name` is used.

        Args:
            name_for_key (str, optional): The name of the API key to select. Defaults to "".
        """
        self.set_api_key_name(name_for_key)

    def get_api_key_name(self) -> str:
        """
        Returns the name of the currently selected API key.

        Returns:
            str: The name of the currently selected API key. If no key is selected, returns an empty string.
        """
        return self.api_key_name

    def set_preferred_api_key_name(self, name: str) -> None:
        """
        Set the preferred API key name in the preferences. To make this permanent,
        the preferences file should be re-written at some point after this.

        Args:
            name (str): The name of the preferred API key.

        Raises:
            KeyError: If the name is not found in the list of API keys.
        """
        name = name.lower()
        try:
            self.api_keys[name]["DEFAULT"] = "1"
        except KeyError:
            raise KeyError(
                f"Can't use name {name} as preferred API key; not in list of keys."
            )

    def set_api_key_name(self, name_for_key: str = "") -> None:
        """
        Set the currently selected API key by name.

        If no name is given, the DEFAULT flag in the preferences file will be used to select the API key.
        If no key is marked as preferred, a random key will be chosen.

        Args:
            name_for_key (str, optional): The name of the API key to select. Defaults to "".

        Raises:
            KeyError: If the name is not found in the list of API keys.
        """

        self.api_key_name = ""
        if not self.api_keys:
            return
        if name_for_key:
            if name_for_key not in self.api_keys:
                raise KeyError(f"Name {name_for_key} not in API key list.")
            self.api_key_name = name_for_key
        else:
            for name in self.api_keys:
                if self.api_keys[name]["DEFAULT"]:
                    if not self.api_key_name:
                        self.api_key_name = name
                    else:
                        self.api_keys[name]["DEFAULT"] = ""
        if not self.api_key_name:
            # Fallback, choose a random name if none preferred.
            self.api_key_name = random.choice(list(self.api_keys.keys()))

    def remove_name(self, name: str) -> None:
        """
        Remove an API key by name from the preferences.

        Args:
            name (str): The name of the API key to remove.

        Raises:
            KeyError: If the name is not found in the list of API keys.
        """
        try:
            self.api_keys.pop(name)
        except KeyError:
            pass

    def write_api_key_preferences_to_file(self) -> None:
        """
        Write the current API key preferences to the config file.

        Before writing, any None values in the preferences dict are replaced with
        empty strings. If the file cannot be written due to a PermissionError,
        the program exits with an error message.

        Returns:
            None
        """
        for name in self.api_keys:
            for cat in self.api_keys[name]:
                if self.api_keys[name][cat] is None:
                    self.api_keys[name][cat] = ""
        try:
            with open(API_KEY_CONFIG_FILE_PATH, "w", encoding="utf8") as fout:
                yaml.dump(self.api_keys, fout)
        except PermissionError:
            print("API config file could not be created due to PermissionError.")
            sys.exit(f"Location is {API_KEY_CONFIG_FILE_PATH}")
