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
    elif response.lower().startswith('n'):
        return False
    else:
        return None


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


def print_break():
    print('----------------------------------')


def pretty_print_input_fields(input_fields):
    for input_field in input_fields:
        input_field_data = input_fields[input_field]
        if input_field == 'header':
            input_field = 'header_row'
        print('{: <12}{}'.format(input_field, input_field_data))


def pretty_print_disqualifying_issues(disqualifying_issues):
    for issue in disqualifying_issues:
        issue_setting = disqualifying_issues[issue]
        print('{: <40}{}'.format(issue, issue_setting))



class BulkConfig(ValidatorConfig):

    file_endings = InputFields.spreadsheet_file_endings.copy()
    marc_file_endings = {'mrk'}

    def __init__(self):
        super().__init__()
        self.program_name = None
        self.associated_names = set()
        self.input_file_type = None
        self.input_fields = {}
        self.disqualifying_issues = OrderedDict()

    def add_new_data_to_config(self):
        self.config['programs'][self.program_name] = {
            'file_type': self.input_file_type,
            'input_fields': {},
            'disqualifying_issues': {}}
        for input_field in self.input_fields:
            self.config['programs'][self.program_name]['input_fields'][input_field] = self.input_fields[input_field]
        for disqualifying_issue in self.disqualifying_issues:
            self.config['programs'][self.program_name]['disqualifying_issues'][disqualifying_issue] = self.disqualifying_issues[disqualifying_issue]


def check_if_program_done_already(program_name, validator_config):
    for program in validator_config.config['programs']:
        if program and program.lower() == program_name.lower():
            question = 'Data for {} found in configurations file. Overwrite? (y/n)'.format(program_name)
            if not get_yes_no_response(question):
                sys.exit('Will not overwrite. Quitting.')
    if program_name.lower() in validator_config.names_associated_to_programs_map:
        associated_program = validator_config.names_associated_to_programs_map[program_name.lower()]
        print('Name {} associated with program {} in config file. Cannot continue with removing this association.'.format(program_name, associated_program))
        question = 'Remove association? (y/n)'
        if get_yes_no_response(question) is True:
            remove_me = set()
            try:
                for i, associated_name in enumerate(validator_config.config['programs'][associated_program]['associated_names']):
                    if associated_name.lower() == program_name.lower():
                        remove_me.add(associated_name)
            except KeyError:
                pass
            for remove_name in remove_me:
                validator_config.config['programs'][associated_program]['associated_names'].remove(remove_name)
        else:
            sys.exit('Will not remove. Quitting.')


def get_program_name(validator_config):
    while True:
        program_name = get_varied_response('Enter program identification:', blank_ok=False)
        if get_yes_no_response("You entered {}. Is this correct?".format(program_name)):
            program_name = program_name.lower()
            check_if_program_done_already(program_name, validator_config)
            print_break()
            return program_name


def enter_associated_names(program_name, program_dict, validator_config):
    associated_names = set()
    while True:
        if not associated_names:
            if not get_yes_no_response('Are there any other names associated with {}?'.format(program_name)):
                return
        associated_name = get_varied_response('Enter associated name.', blank_ok=True)
        if associated_name:
            if associated_name.lower() in validator_config.config['programs']:
                print('Name {} found as program name in configuration file. Skipping.'.format(associated_name))
            elif associated_name.lower() in validator_config.names_associated_to_programs_map:
                associated_program = validator_config.names_associated_to_programs_map[associated_name.lower()]
                print('Name {} found associated to program name {} in configuration file. Skipping.'.format(associated_name, associated_program))
            else:
                print('Adding {} to {}.'.format(associated_name, program_name))
                associated_names.add(associated_name.lower())
        else:
            print('No associated name added.')
        if not get_yes_no_response('Add another name?'):
            print('Associating the following names with {}.'.format(program_name))
            for associated_name in associated_names:
                print(associated_name)
            if not get_yes_no_response('OK?'):
                print('Associating no names with {}.'.format(program_name))
                associated_names = {}
            program_dict['associated_names'] = list(associated_names)
            return


def get_input_filetype(program_name, program_dict):
    while True:
        valid_responses = {'1': 'MARC', '2': 'spreadsheet'}
        print('What type of input files will {} send?'.format(program_name))
        print('1. MARC')
        print('2. Spreadsheet (xlsx, txt, tsv, or csv)')
        response = get_varied_response('Choose 1 or 2.', valid_responses=valid_responses, blank_ok=False)
        if get_yes_no_response('You chose {}, {}. Correct?'.format(response, valid_responses[response])):
            input_file_type = valid_responses[response]
            program_dict['file_type'] = input_file_type
            print_break()
            return


def get_input_fields(program_name, program_dict):
    print('Choose input field locations for {}.'.format(program_name))
    while True:
        program_dict['input_fields'] = {}
        if program_dict['file_type'] == 'MARC':
            get_marc_input_fields(program_dict)
        elif program_dict['file_type']  == 'spreadsheet':
            get_spreadsheet_input_fields()
        print('Your choices:')
        pretty_print_input_fields(program_dict['input_fields'])
        if get_yes_no_response('Is this correct?'):
            print_break()
            return    


def get_marc_input_fields(program_dict):
    input_fields_list = InputFields.marc_cats.copy()
    print('Enter fields in the form "590" or "907a".')

    for input_field in input_fields_list:
        if input_field == '863':
            if get_yes_no_response('Holdings in 863/864/865? (y/n)') is True:
                program_dict['input_fields'][input_field] = 1
            else:
                program_dict['input_fields'][input_field] = 0
        elif input_field == '866':
            if get_yes_no_response('Holdings in 866/867/868? (y/n)') is True:
                program_dict['input_fields'][input_field] = 1
            else:
                program_dict['input_fields'][input_field] = 0
        elif input_field == '583':
            if get_yes_no_response('File has 583s? (y/n)') is True:
                program_dict['input_fields'][input_field] = 1
            else:
                program_dict['input_fields'][input_field] = 0                
        else:
            if input_field == 'holdings_1' or input_field == 'holdings_2':
                response = get_varied_response('other holdings field'.format(input_field))
            else:
                response = get_varied_response('{} field'.format(input_field))
            program_dict['input_fields'][input_field] = response


def get_spreadsheet_input_fields(program_dict):
    input_fields = InputFields.spreadsheet_cats.copy()
    print('Note that columns are counted from 1, not zero.')
    print('If a field is not in the input file, leave it blank.')
    for input_field in input_fields:
        if input_field == 'header':
            if get_yes_no_response('Is the header in the first row? (y/n)'):
                program_dict['input_fields'][input_field] = 1
            else:
                program_dict['input_fields'][input_field] = 0
        else:
            response = get_varied_response('Column for {}:'.format(input_field), blank_ok=True)
            program_dict['input_fields'][input_field] = response


def choose_disqualifying_issues(program_name, program_dict, validator_config):
    while True:
        default_disqualifying_issues = validator_config.get_default_disqualifying_issues()
        if get_yes_no_response('Use default disqualifying issues for {}?'.format(program_name)):
            program_dict['disqualifying_issues'] = dict(default_disqualifying_issues)
        else:
            print('Choosing disqualifying issues. Please enter 1 for True or 0 for False, or return to accept the default.')
            valid_responses = {'0', '1'}
            program_dict['disqualifying_issues'] = {}
            for issue in default_disqualifying_issues:
                default_response = default_disqualifying_issues[issue]
                response = get_varied_response(
                    '{} [default {}]'.format(issue, default_response), valid_responses=valid_responses, blank_ok=True)
                if response in valid_responses:
                    if response == '1':
                        program_dict['disqualifying_issues'][issue] = True
                    else:
                        program_dict['disqualifying_issues'][issue] = False
                else:
                    program_dict['disqualifying_issues'][issue] = default_response
        print('Your choices:')
        pretty_print_disqualifying_issues(program_dict['disqualifying_issues'])
        if get_yes_no_response('Is this correct?'):
            return        


def run_bulk_config():

    validator_config = ValidatorConfig()
    program_name = get_program_name(validator_config)
    program_dict = {}
    enter_associated_names(program_name, program_dict, validator_config)
    get_input_filetype(program_name, program_dict)
    get_input_fields(program_name, program_dict)
    choose_disqualifying_issues(program_name, program_dict, validator_config)

    while True:
        add_response = get_yes_no_response('Add data for {} to configuration file? (y/n)'.format(program_name))
        if add_response is True:
            print('Adding data for program {} to configuration file.'.format(program_name))
            validator_config.config['programs'][program_name] = program_dict
            validator_config.write_validator_config_file()
            break
        elif add_response is False:
            print('Will not add data to configuration file. Quitting.')
            break
        else:
            print('Please enter "y" or "n".')
