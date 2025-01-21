import os
import sys
from unicodedata import name
from termcolor import colored, cprint
import typing

import crl_lib.api_keys


IS_SEARCH_API_KEY_VALUE = colored("Search", "green")
IS_METADATA_API_KEY_VALUE = colored("Metadata", "cyan")
IS_DEFAULT_KEY_VALUE = "  " + colored("default", "white", "on_blue") + "  "
IS_NOT_DEFAULT_KEY_VALUE = "           "

SUCCESS_LINE = "Key " + colored("works", "yellow") + " with {} API."
FAILURE_LINE = "Key " + colored("does not work", "red") + " with {} API."
NOT_SET_LINE = FAILURE_LINE + " " + colored("{} not set.", "red")

HORIZONTAL_LINE = "".join(["-" for i in range(0, 109)])


def print_terminal_page_header(header_str: str) -> None:
    """
    Prints a header string to the terminal, surrounded by green
    "~~~~~~~~~~~~" bars and followed by a blank line.

    Args:
        header_str (str): The string to print as the header.
    """

    header_bar = "".join(["~" for _ in header_str])
    cprint(header_bar, "green")  # type: ignore[arg-type]
    cprint(header_str, "green")  # type: ignore[arg-type]
    cprint(header_bar, "green")  # type: ignore[arg-type]
    print("")


class ApiKeySetter:
    """
    A class to manage API keys through a terminal-based GUI. 
    The ApiKeySetter class provides functionality to read, write, and manage API keys
    using a terminal-based graphical user interface. It allows users to add, remove,
    set default, and test API keys. The class interacts with the OclcApiKeys library
    to perform these operations.
    """

    def __init__(self) -> None:
        self.api_key_names: typing.List[str] = []
        self.create_gui()

    @staticmethod
    def print_row_to_terminal(
        number_column: str,
        name: str,
        api_key: str,
        api_secret: str,
        for_which_apis: str,
        is_default_print: str,
        header_row: bool = False,
    ) -> None:
        """
        Prints a row of a table to the terminal, with the given
        data.

        If header_row is True, prints a horizontal line instead.

        Args:
            number_column (str): The number to print in the first column
            name (str): The name of the API key.
            api_key (str): The API key itself.
            api_secret (str): The API secret.
            for_which_apis (str): A string indicating which APIs the key
                works with.
            is_default_print (str): A string indicating whether the key
                is the default key.
            header_row (bool): If True, print a horizontal line instead of
                a row of data.
        """
        if header_row is True:
            print(HORIZONTAL_LINE)
            return

        first_col = f'{colored(number_column, "yellow").ljust(3)}{is_default_print}'

        print(f'{first_col}{name.ljust(12)}{colored("Key", "yellow")}: {api_key}')
        print(f'                        {colored("Secret", "yellow")}: {api_secret}')
        print(f'                        {colored("APIs", "yellow")}: {for_which_apis}')

        print(HORIZONTAL_LINE)

    def make_which_apis_work_with_key_print_string(self, name: str) -> str:
        """
        Constructs a string indicating which APIs the given API key works with.

        Args:
            name (str): The name of the API key.

        Returns:
            str: A comma-separated string listing the APIs the key works with,
            formatted with color for terminal display.
        """

        return_string_list = []
        if self.api_key_manager.api_keys[name]["SEARCH"]:
            return_string_list.append(IS_SEARCH_API_KEY_VALUE)
        if self.api_key_manager.api_keys[name]["METADATA"]:
            return_string_list.append(IS_METADATA_API_KEY_VALUE)
        return ", ".join(return_string_list)

    def create_gui(self) -> None:
        """
        Main loop of the GUI. Prints the current keys and their properties to
        the terminal, and then asks the user what to do.

        The user can add a new key, remove a key, set a new default key, test
        all the keys, go back to the main menu, or quit the program.

        The loop continues until the user chooses to go back to the main menu
        or quit the program.
        """
        while True:
            self.api_key_manager = crl_lib.api_keys.OclcApiKeys()

            os.system("cls" if os.name == "nt" else "clear")

            print_terminal_page_header("Set API Keys")

            self.api_key_names = list(self.api_key_manager.api_keys.keys())
            self.api_key_names.insert(0, "")

            self.print_row_to_terminal(
                " ", "Name", "API Key", "API Secret", "APIs", "", header_row=True
            )

            for i in range(1, len(self.api_key_names)):
                name = self.api_key_names[i]
                if not name:
                    continue
                api_key = self.api_key_manager.api_keys[name]["KEY"]
                api_secret = self.api_key_manager.api_keys[name]["SECRET"]

                if self.api_key_manager.api_keys[name]["DEFAULT"] == "1":
                    is_default_print = IS_DEFAULT_KEY_VALUE
                else:
                    is_default_print = IS_NOT_DEFAULT_KEY_VALUE

                which_apis_print = self.make_which_apis_work_with_key_print_string(name)

                self.print_row_to_terminal(
                    str(i),
                    name,
                    api_key,
                    api_secret,
                    which_apis_print,
                    is_default_print,
                )

            print("")
            print("{}. Add a new key.".format(colored("a", "yellow")))
            print("{}. Remove a key.".format(colored("r", "yellow")))
            print("{}. Set a new default key.".format(colored("d", "yellow")))
            print("{}. Test the keys.".format(colored("t", "yellow")))
            print("{}. Back to the main menu.".format(colored("m", "yellow")))
            print("{}. Quit the program.".format(colored("q", "yellow")))
            print("")
            choice_result = input("Your choice? ")

            if choice_result.lower() == "a":
                self.add_key()

            elif choice_result.lower() == "r":
                self.delete_key()

            elif choice_result.lower() == "d":
                self.set_default_key()

            elif choice_result.lower() == "t":
                self.test_all_api_keys()

            elif choice_result.lower() == "m":
                break
            elif choice_result.lower() == "q":
                sys.exit()
            else:
                print("I didn't understand that.")
            print("")

    def add_key(self) -> None:
        """
        Prompts the user to enter details for a new API key and adds it to the API key manager.

        This function collects the name, API key, secret, and whether the key should be the default from the user.
        It then checks if the key works with the search and metadata APIs and adds the key to the API key manager.

        If no name, key, or secret is provided, the key is not added.

        The user must press Enter to continue after the key is added.

        Returns:
            None
        """
        new_name = input("{} name for key: ".format(colored("Enter", "yellow")))
        new_key = input("{} API key: ".format(colored("Enter", "yellow")))
        new_secret = input(
            "{} API secret (if applicable): ".format(colored("Enter", "yellow"))
        )
        new_is_default = input(
            "Make default key? ({}/{}) ".format(
                colored("y", "yellow"), colored("n", "yellow")
            )
        )
        new_is_default = True if new_is_default.lower().startswith("y") else False

        if not new_name:
            print("No name given; key not added.")
        elif not new_key:
            print("No key input; nothing added.")
        elif not new_secret:
            print("No secret input; nothing added.")
        else:
            new_is_search = crl_lib.api_keys.check_key_on_search_api(
                new_key, new_secret
            )
            new_is_metadata = crl_lib.api_keys.check_key_on_metadata_api(
                new_key, new_secret
            )
            self.api_key_manager.add_or_update_api_key(
                name=new_name,
                my_key=new_key,
                my_secret=new_secret,
                is_search=new_is_search,
                is_metadata=new_is_metadata,
                is_default=new_is_default,
                is_new_key=True,
            )
            input("Press Enter to continue.")

    def delete_key(self) -> None:
        """
        Ask user which API key to delete.

        This function is part of the interactive API key manager. It asks the
        user to enter the number of the API key they want to delete, and then
        deletes it from the preferences file.

        Args:
            None

        Returns:
            None
        """
        to_delete = input("{} number to delete: ".format(colored("Enter", "yellow")))
        try:
            name_to_delete = self.api_key_names[int(to_delete.strip())]
            try:
                self.api_key_manager.api_keys.pop(name_to_delete)
                self.api_key_manager.write_api_key_preferences_to_file()
            except IndexError:
                pass
        except (ValueError, TypeError, IndexError):
            print("Must enter a valid number to delete.")
            input("Press Enter to continue.")

    def set_default_key(self) -> None:
        """
        Ask user which API key to set as default.

        This function is part of the interactive API key manager. It asks the
        user to enter the number of the API key they want to set as default, and
        then sets that key as the default.

        Args:
            None

        Returns:
            None
        """

        new_default = input(
            "{} number to set as default: ".format(colored("Enter", "yellow"))
        )
        try:
            default_name = self.api_key_names[int(new_default)]
            for name in self.api_key_manager.api_keys:
                self.api_key_manager.api_keys[name]["DEFAULT"] = ""
            self.api_key_manager.api_keys[default_name]["DEFAULT"] = "1"
            self.api_key_manager.write_api_key_preferences_to_file()
        except (ValueError, TypeError, IndexError):
            print("Must enter a number to set default key.")
            input("Press Enter to continue.")

    def test_all_api_keys(self) -> None:
        """
        Test all API keys in the preferences file to see if they work.

        This function is part of the interactive API key manager. It tests all
        the API keys in the preferences file to see if they work with both the
        Search and Metadata APIs. It prints out a line for each API key showing
        whether or not it works with each API. If any of the API keys don't have
        a key or secret set, it prints a line saying which one is missing.

        If any of the API keys were previously marked as working with an API but
        now don't, or previously marked as not working but now do, this function
        will update the preferences file with the new values.

        Args:
            None

        Returns:
            None
        """
        changed = False
        for name in self.api_key_manager.api_keys:
            cprint(f"Testing {name}...", "white", "on_blue")
            my_key = self.api_key_manager.api_keys[name]["KEY"]
            my_secret = self.api_key_manager.api_keys[name]["SECRET"]
            works_with_metadata = crl_lib.api_keys.check_key_on_metadata_api(
                my_key, my_secret
            )
            works_with_search = crl_lib.api_keys.check_key_on_search_api(
                my_key, my_secret
            )

            if not my_key or not my_secret:
                if not my_key:
                    print(NOT_SET_LINE.format("Metadata and Search", "API key"))
                if not my_secret:
                    print(NOT_SET_LINE.format("Metadata and Search", "API key secret"))
                continue

            if works_with_metadata:
                print(SUCCESS_LINE.format("Metadata"))
            else:
                print(FAILURE_LINE.format("Metadata"))
            if works_with_search:
                print(SUCCESS_LINE.format("Search"))
            else:
                print(FAILURE_LINE.format("Search"))

            if self.api_key_manager.api_keys[name]["METADATA"] != works_with_metadata:
                self.api_key_manager.api_keys[name]["METADATA"] = works_with_metadata
                changed = True
            if self.api_key_manager.api_keys[name]["SEARCH"] != works_with_search:
                self.api_key_manager.api_keys[name]["SEARCH"] = works_with_search
                changed = True

        if changed is True:
            self.api_key_manager.write_api_key_preferences_to_file()
        input("Press Enter to continue.")


if __name__ == "__main__":
    a = ApiKeySetter()
