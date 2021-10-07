import os
import sys
import yaml
from pprint import pprint
from collections import OrderedDict

from validator_lib.validator_config import ValidatorConfig
from validator_lib.choose_input_file_fields import InputFields


def get_yes_no_response(question):
    response = input(question + '  ')
    if response.lower().startswith('y'):
        return True
    return False


def get_varied_response(question, valid_responses=None, blank_ok=True):
    while True:
        response = input(question + '  ')
        response = response.strip()
        if not response and blank_ok is True:
            return response
        if not valid_responses:
            return response
        if response in valid_responses:
            return response
        print('Invalid response.')    


class BulkConfig:
    default_disqualifying_issues = ValidatorConfig.get_default_disqualifying_issues()
    file_endings = InputFields.spreadsheet_file_endings.copy()
    marc_file_endings = {'mrk'}
    bulk_config_file = os.path.join(os.getcwd(), 'data', 'bulk_config.yaml')

    def __init__(self):
        self.program_name = None
        self.associated_names = set()
        self.associated_names_map = {}
        self.input_file_type = None
        self.input_fields = {}
        self.disqualifying_issues = OrderedDict()
        self.read_config_file()

    @staticmethod
    def print_break():
        print('----------------------------------')

    def read_config_file(self):
        if not os.path.isfile(self.bulk_config_file):
            with open(self.bulk_config_file, 'w', encoding='utf8') as fout:
                pass
        with open(self.bulk_config_file, 'r', encoding='utf8') as fin:
            self.bulk_config_data = yaml.load(fin, Loader=yaml.FullLoader)
        if not self.bulk_config_data:
            self.bulk_config_data = {}
        for program in self.bulk_config_data:
            program = program.lower()
            if not program:
                continue
            for associated_name in self.bulk_config_data[program]['associated_names']:
                if not associated_name:
                    continue
                self.associated_names_map[associated_name.lower()] = program

    def write_bulk_config_data(self):
        self.bulk_config_data[self.program_name]['associated_names'] = list(self.associated_names.copy())
        with open(self.bulk_config_file, 'w', encoding='utf8') as fout:
            yaml.dump(self.bulk_config_data, fout)

    def add_new_data_to_config(self):
        self.bulk_config_data[self.program_name] = {
            'file_type': self.input_file_type,
            'input_fields': {},
            'disqualifying_issues': {}}
        for input_field in self.input_fields:
            self.bulk_config_data[self.program_name]['input_fields'][input_field] = self.input_fields[input_field]
        for disqualifying_issue in self.disqualifying_issues:
            self.bulk_config_data[self.program_name]['disqualifying_issues'][disqualifying_issue] = self.disqualifying_issues[disqualifying_issue]

    def get_program_name(self):
        while True:
            program_name = get_varied_response('Enter program identification:', blank_ok=False)
            if get_yes_no_response("You entered {}. Is this correct?".format(program_name)):
                self.program_name = program_name.lower()
                self.check_if_program_done_already()
                self.print_break()
                break

    def check_if_program_done_already(self):
        for program in self.bulk_config_data:
            if program and program.lower() == self.program_name.lower():
                question = 'Data for {} found in configurations file. Overwrite? (y/n)'.format(self.program_name)
                if not get_yes_no_response(question):
                    sys.exit('Will not overwrite. Quitting.')
        if self.program_name.lower() in self.associated_names_map:
            associated_program = self.associated_names_map[self.program_name.lower()]
            print('Name {} associated with program {} in config file. Cannot continue with removing this association.'.format(self.program_name, associated_program))
            question = 'Remove association? (y/n)'
            if get_yes_no_response(question) is True:
                remove_me = set()
                for i, associated_name in enumerate(self.bulk_config_data[associated_program]['associated_names']):
                    if associated_name.lower() == self.program_name.lower():
                        remove_me.add(associated_name)
                for remove_name in remove_me:
                    self.bulk_config_data[associated_program]['associated_names'].remove(remove_name)
            else:
                sys.exit('Will not remove. Quitting.')

    def enter_associated_names(self):
        while True:
            if not self.associated_names:
                if not get_yes_no_response('Are there any other names associated with {}?'.format(self.program_name)):
                    return
            associated_name = get_varied_response('Enter associated name.', blank_ok=True)
            if associated_name:
                if associated_name.lower() in self.bulk_config_data:
                    print('Name {} found in configuration file. Skipping.'.format(associated_name))
                else:
                    print('Adding {} to {}.'.format(associated_name, self.program_name))
                    self.associated_names.add(associated_name.lower())
            else:
                print('No associated name added.')
            if not get_yes_no_response('Add another name?'):
                print('Associating the following names with {}.'.format(self.program_name))
                for associated_name in self.associated_names:
                    print(associated_name)
                if not get_yes_no_response('OK?'):
                    print('Associating no names with {}.'.format(self.program_name))
                    self.associated_names = {}
                break

    def get_input_filetype(self):
        while True:
            valid_responses = {'1': 'MARC', '2': 'spreadsheet'}
            print('What type of input files will {} send?'.format(self.program_name))
            print('1. MARC')
            print('2. Spreadsheet (xlsx, txt, tsv, or csv)')
            response = get_varied_response('Choose 1 or 2.', valid_responses=valid_responses, blank_ok=False)
            if get_yes_no_response('You chose {}, {}. Correct?'.format(response, valid_responses[response])):
                self.input_file_type = valid_responses[response]
                self.print_break()
                break

    def get_input_fields(self):
        print('Choose input field locations for {}.'.format(self.program_name))
        while True:
            if self.input_file_type == 'MARC':
                self.get_marc_input_fields()
            elif self.input_file_type == 'spreadsheet':
                self.get_spreadsheet_input_fields()
            print('Your choices:')
            self.pretty_print_input_fields()
            if get_yes_no_response('Is this correct?'):
                self.print_break()
                break    

    def get_marc_input_fields(self):
        input_fields = InputFields.marc_cats.copy()
        print('Enter fields in the form "590" or "907a".')

        for input_field in input_fields:
            if input_field == '863':
                if get_yes_no_response('Holdings in 863/864/865? (y/n)') is True:
                    self.input_fields[input_field] = 1
                else:
                    self.input_fields[input_field] = 0
            elif input_field == '866':
                if get_yes_no_response('Holdings in 866/867/868? (y/n)') is True:
                    self.input_fields[input_field] = 1
                else:
                    self.input_fields[input_field] = 0
            elif input_field == '583':
                if get_yes_no_response('File has 583s? (y/n)') is True:
                    self.input_fields[input_field] = 1
                else:
                    self.input_fields[input_field] = 0                
            else:
                if input_field == 'holdings_1' or input_field == 'holdings_2':
                    response = get_varied_response('other holdings field'.format(input_field))
                else:
                    response = get_varied_response('{} field'.format(input_field))
                self.input_fields[input_field] = response

    def get_spreadsheet_input_fields(self):
        input_fields = InputFields.spreadsheet_cats.copy()
        print('Note that columns are counted from 1, not zero.')
        print('If a field is not in the input file, leave it blank.')
        for input_field in input_fields:
            if input_field == 'header':
                if get_yes_no_response('Is the header in the first row? (y/n)'):
                    self.input_fields[input_field] = 1
                else:
                    self.input_fields[input_field] = 0
            else:
                response = get_varied_response('Column for {}:'.format(input_field), blank_ok=True)
                self.input_fields[input_field] = response

    def choose_disqualifying_issues(self):
        while True:
            if get_yes_no_response('Use default disqualifying issues for {}?'.format(self.program_name)):
                self.copy_default_issues()
            else:
                print('Choosing disqualifying issues. Please enter 1 for True or 0 for False, or return to accept the default.')
                valid_responses = {'0', '1'}
                for issue in self.default_disqualifying_issues:
                    default_response = self.default_disqualifying_issues[issue]
                    response = get_varied_response(
                        '{} [default {}]'.format(issue, default_response), valid_responses=valid_responses, blank_ok=True)
                    if response in valid_responses:
                        if response == '1':
                            self.disqualifying_issues[issue] = True
                        else:
                            self.disqualifying_issues[issue] = False
                    else:
                        self.disqualifying_issues[issue] = default_response
            print('Your choices:')
            self.pretty_print_disqualifying_issues()
            if get_yes_no_response('Is this correct?'):
                break        

    def copy_default_issues(self):
        self.disqualifying_issues = self.default_disqualifying_issues.copy()

    def pretty_print_input_fields(self):
        for input_field in self.input_fields:
            input_field_data = self.input_fields[input_field]
            if input_field == 'header':
                input_field = 'header_row'
            print('{: <12}{}'.format(input_field, input_field_data))

    def pretty_print_disqualifying_issues(self):
        for issue in self.disqualifying_issues:
            issue_setting = self.disqualifying_issues[issue]
            print('{: <40}{}'.format(issue, issue_setting))

    def run_bulk_config(self):
        self.get_program_name()
        self.enter_associated_names()
        self.get_input_filetype()
        self.get_input_fields()
        self.choose_disqualifying_issues()


def run_bulk_config():
    bulk_config = BulkConfig()
    bulk_config.run_bulk_config()
    bulk_config.add_new_data_to_config()
    bulk_config.write_bulk_config_data()
