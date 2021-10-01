"""
Basic interface for the CRL Serials Validator.

Usage:

    python crl_serials_validator.py  # run the Validator with a command-line interface
    python crl_serials_validator.py -a  # run the Validator in automated (headless) mode
    python crl_serials_validator.py --headless  # run the Validator in automated (headless) mode
    python crl_serials_validator.py -b  # set bulk/automated/headless mode preferences
    python crl_serials_validator.py --bulk_prefs  # set bulk/automated/headless mode preferences
    python crl_serials_validator.py -s  # set WorldCat Search API keys on the command line
    python crl_serials_validator.py --set_keys  # set WorldCat Search API keys on the command line
    python crl_serials_validator.py -p my_filename.tsv  # process a single specifid file
    
"""

import sys
import os
import argparse
from tkinter import Label, ttk
import tkinter as tk
from contextlib import redirect_stdout
import io

from validator_lib.validator_controller import ValidatorController
from validator_lib.bulk_validator_preferences import run_bulk_config
from validator_lib.command_line_api_keys import CommandLineApiKeys
from validator_lib.ttk_theme import set_ttk_style


class ValidatorTkinterInterface(tk.Tk):
    """
    Basic GUI interface for the Validator.
    """

    docs_text = 'Visit the documentation in a web browser'
    api_text = 'Set up your WorldCat Search API keys'
    scan_text = 'Do a quick scan of any MARC input files to find important fields'
    fields_text = 'Specify fields in input files'
    issues_text = 'Specify disqualifying issues'
    process_text = 'Process input and WorldCat MARC to create outputs'

    def __init__(self):
        super().__init__()

        self.validator_controller = ValidatorController()

        style = set_ttk_style()

        self.issn_database_note_printed = False

        self.resizable(1, 1)
        self.title('CRL Serials Validator')
    
        ttk.Button(text=self.api_text, style='primary.TButton', command=self.run_api_keys).pack(padx=5, pady=5, fill='x')
        ttk.Button(text=self.scan_text, style='primary.TButton', command=self.scan_files).pack(padx=5, pady=5, fill='x')
        ttk.Button(text=self.fields_text, style='primary.TButton', command=self.select_fields).pack(padx=5, pady=5, fill='x')
        ttk.Button(text=self.issues_text, style='primary.TButton', command=self.select_issues).pack(padx=5, pady=5, fill='x')
        ttk.Button(text=self.process_text, style='primary.TButton', command=self.process_files).pack(padx=5, pady=5, fill='x')
        ttk.Button(text=self.docs_text, style='info.TButton', command=self.load_docs).pack(padx=5, pady=5, fill='x')

        ttk.Button(text='Quit', style="warning.TButton", command=self.cancel).pack(padx=5, pady=5)

        self.mainloop()

    def run_api_keys(self):
        self.cancel()
        self.validator_controller.set_api_keys()
        self.create_main_window()

    def scan_files(self):
        """
        Temporary working version with redirected output.
        """
        self.cancel()
        f = io.StringIO()
        with redirect_stdout(f):
            self.validator_controller.scan_input_files()
        s = f.getvalue()
        print(s)
        w = tk.Tk()
        ttk.Label(w, text=s).pack()
        w.mainloop()
        self.create_main_window()

    def select_fields(self):
        self.cancel()
        self.validator_controller.choose_input_fields()
        self.create_main_window()

    def select_issues(self):
        self.cancel()
        self.validator_controller.set_disqualifying_issues()
        self.create_main_window()

    def process_files(self):
        self.cancel()
        self.validator_controller.run_checks_process()
        self.create_main_window()

    def load_docs(self):
        self.validator_controller.open_project_docs()

    def cancel(self):
        self.destroy()

    def create_main_window(self):
        self.__init__()



class SimpleValidatorInterface:
    """
    A very simple command line interface for the Validator.

    Asks "what next?" then triggers the ValidatorController to run the appropriate actions.
    """

    def __init__(self):

        self.args = parse_command_line_args()
        self.controller = ValidatorController(headless_mode=False)

        question_map = self.get_question_map()

        while True:
            response = self.get_wanted_action(question_map)
            if response == "visit_docs":
                self.controller.open_project_docs()
            elif response == "set_key":
                self.controller.set_api_keys()
            elif response == "scan_inputs":
                self.controller.scan_input_files()
                self.command_line_pause()
            elif response == "set_input":
                self.controller.choose_input_fields()
            elif response == "set_issues":
                self.controller.set_disqualifying_issues()
            elif response == "process_data":
                error_message, warning_messages = self.controller.check_if_run_is_possible()
                if error_message:
                    print('')
                    print('ERROR: {}'.format(error_message))
                    self.command_line_pause()
                else:
                    if warning_messages:
                        for warning_message in warning_messages:
                            print('WARNING: {}'.format(warning_message))
                        continue_check = input("Run the process anyway? (Y/N)")
                        if not continue_check.lower().startswith('y'):
                            self.command_line_pause()
                            continue
                    self.controller.run_checks_process()
            elif response == "quit":
                print("Quitting.")
                sys.exit()

    @staticmethod
    def clear_screen():
        """Clear the screen so that there isn't an endless scroll of the question list."""
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")

    def get_wanted_action(self, question_map):
        """
        Print out the question list and get a response.
        """
        while True:
            print("\nWhat would you like to do?")
            for i in range(1, len(question_map)):
                print("{}. {}".format(i, question_map[i][0]))
            print("q. Quit.")
            input_result = input()
            input_result = input_result.strip()
            if input_result.lower() == "q":
                return "quit"
            if input_result.isdigit():
                try:
                    response = question_map[int(input_result)][1]
                    return response
                except IndexError:
                    print("I didn't understand that.")
                    self.command_line_pause()
                    self.clear_screen()

    def get_question_map(self):
        """
        Get the list of appropriate questions. It only allows for questions relating to the set if relevant data is
        seen in the input folder.
        """
        question_map = [""]
        question_map.append(("Visit the Validator documentation in a web browser.", "visit_docs"))
        question_map.append(("Set up your WorldCat Search API keys.", "set_key"))
        if self.controller.input_files_seen:
            if self.controller.marc_input_seen:
                question_map.append(
                    ("Do a quick scan of any MARC input files to find important fields.", "scan_inputs")
                )
            question_map.append(("Specify fields in input files.", "set_input"))
            question_map.append(("Specify disqualifying issues.", "set_issues"))
            question_map.append(("Process input and WorldCat MARC to create outputs.", "process_data"))
        return question_map

    @staticmethod
    def command_line_pause():
        """Pause."""
        input("\nPress Enter to continue.")

    @staticmethod
    def get_stripped_input(question_list):
        """Ask a question, get the response without linebreaks."""
        question_str = "\n".join(question_list)
        print(question_str)
        input_result = input()
        return input_result.strip()


def parse_command_line_args():
    parser = argparse.ArgumentParser(description="Validate shared print holdings data.")
    parser.add_argument("--headless", "-a", action="store_true", help="Run in headless (automated) mode.")
    parser.add_argument("--graphical", "-g", action="store_true", help="Run in graphical (GUI) mode. (Experimental)")
    parser.add_argument("--bulk_prefs", "-b", action="store_true", help="Set bulk (headless) preferences.")
    parser.add_argument("--set_keys", "-s", action="store_true", help="Set API keys on the command line.")
    parser.add_argument("-p", nargs=1, help="Process this single record.")
    args = parser.parse_args()
    return args


def headless_app():
    """
    Headless/bulk mode works by getting every file in the input folder, then running each file individually.
    """
    input_files = os.listdir('input')
    for input_file in input_files:
        file_ext = os.path.split(input_file)[-1].split('.')[-1].lower()
        if file_ext in {'mrk', 'txt', 'tsv', 'csv', 'xlsx'}:
            vc = ValidatorController(headless_mode=True, single_file_run=input_file)
            del(vc)


def headless_api_keys():
    CommandLineApiKeys()


def bulk_preferences():
    run_bulk_config()


def gui_app():
    ValidatorTkinterInterface()


def command_line_app():
    SimpleValidatorInterface()


def process_single_file(filename):
    ValidatorController(headless_mode=True, single_file_run=filename)


if __name__ == "__main__":
    args = parse_command_line_args()

    if args.p:
        process_single_file(args.p[0])
    elif args.set_keys is True:
        headless_api_keys()
    elif args.bulk_prefs is True:
        bulk_preferences()
    elif args.headless is True:
        headless_app()
    elif args.graphical is True:
        gui_app()
    else:
        command_line_app()
