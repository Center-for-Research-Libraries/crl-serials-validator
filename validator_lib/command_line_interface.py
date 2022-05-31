import sys
import os
from termcolor import colored, cprint

from validator_lib.validator_controller import ValidatorController


class SimpleValidatorInterface:
    """
    A very simple command line interface for the Validator.

    Asks "what next?" then triggers the ValidatorController to run the 
    appropriate actions.
    """

    def __init__(self, args):

        self.args = args
        self.controller = ValidatorController(
            headless_mode=False, papr_output=self.args.papr)

        question_map = self.get_question_map()
        
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            response = self.get_wanted_action(question_map)
            if response == "quit":
                print("Quitting.")
                sys.exit()
            os.system('cls' if os.name == 'nt' else 'clear')
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
                    input('Press enter to continue.')

    def get_wanted_action(self, question_map):
        """
        Print out the question list and get a response.
        """
        while True:
            cprint('Welcome to the CRL Serials Validator', 'white', 'on_blue')
            print('')
            cprint('What would you like to do?', 'cyan')
            for i in range(1, len(question_map)):
                print("{}. {}".format(
                    colored(str(i), 'yellow'), question_map[i][0]))
            print("{}. Quit.".format(colored('q', 'yellow')))
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
            os.system('cls' if os.name == 'nt' else 'clear')

    def get_question_map(self):
        """
        Get the list of appropriate questions. It only allows for questions 
        relating to the set if relevant data is seen in the input folder.
        """
        question_map = [""]
        question_map.append(
            ("Visit the Validator documentation in a web browser.",
             "visit_docs"))
        question_map.append(
            ("Set up your WorldCat Search API keys.", "set_key"))
        if self.controller.input_files_seen:
            if self.controller.marc_input_seen:
                question_map.append(
                    ("Do a quick scan of any MARC input files to find important fields.",
                    "scan_inputs")
                )
            question_map.append(("Specify fields in input files.", "set_input"))
            question_map.append(("Specify disqualifying issues.", "set_issues"))
            question_map.append(
                ("Process input and WorldCat MARC to create outputs.",
                "process_data"))
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
