import os
import configparser
import re
from collections import OrderedDict

from validator_lib.bulk_validator_preferences import BulkConfig

class ValidatorConfig:
    def __init__(self):
        self.config = configparser.SafeConfigParser()
        data_folder = os.path.join(os.getcwd(), 'data')
        self.project_config_file = os.path.join(data_folder, 'validator_config.ini')
        self.config_data = {}
        self.read_validator_config_file()
        self.check_that_all_issues_are_in_config()

    def read_validator_config_file(self):
        # create a blank file if none exists
        if not os.path.isfile(self.project_config_file):
            self.write_validator_config_file()
        self.config.read(self.project_config_file)
        if 'disqualifying_issues' not in self.config:
            self.config['disqualifying_issues'] = self.get_default_disqualifying_issues()

    def write_validator_config_file(self):
        if 'Validator' not in self.config:
            self.config['Validator'] = {'jstor': '0'}
        with open(self.project_config_file, "w") as config_out:
            self.config.write(config_out)

    def get_input_fields(self, input_file):
        input_fields = {}
        if input_file not in self.config:
            return input_fields
        for cat in self.config[input_file]:
            if not self.config[input_file][cat]:
                continue
            cat_data = self.config[input_file][cat]
            cat_data = cat_data.strip()
            if input_file.endswith('mrk'):
                cat_data = self.zero_fill_marc_fields(cat_data)
            input_fields[cat] = cat_data
        return input_fields

    def check_that_all_issues_are_in_config(self):
        default_issues = self.get_default_disqualifying_issues()
        changed_issues = False
        for issue in default_issues:
            if issue not in self.config['disqualifying_issues']:
                print('NO {}'.format(issue))
                self.config['disqualifying_issues'][issue] = '0'
                changed_issues = True
        for issue in self.config['disqualifying_issues']:
            if issue not in default_issues:
                self.config['disqualifying_issues'].pop(issue)
                changed_issues = True
        if changed_issues:
            self.write_validator_config_file()

    @staticmethod
    def zero_fill_marc_fields(field):
        if not field:
            return ''
        if str(field).isdigit():
            return str(field).zfill(3)
        m = re.search(r'^ *(\d+)([a-z]) *$', str(field).lower())
        if not m:
            return field
        field_digits = m.group(1)
        field_letter = m.group(2)
        field = field_digits.zfill(3) + field_letter
        return field

    @staticmethod
    def get_default_disqualifying_issues():
        disqualifying_issues = OrderedDict({
            'bib_lvl_not_serial': 1,
            'form_not_print': 1,
            'record_type_not_language_material': 1,
            'serial_type_not_periodical': 1,
            'invalid_carrier_type': 1,
            'invalid_media_type': 1,
            'issn_db_form_not_print': 1,
            'issn_db_serial_type_not_periodical': 1,
            'no_oclc_number': 1,
            'no_worldcat_record': 1,

            'binding_words_in_holdings': 1,
            'completeness_words_in_holdings': 1,
            'nonprint_words_in_holdings': 1,

            'title_in_jstor': 0,

            'duplicate_holdings_id': 1,
            'duplicate_local_oclc': 1,
            'duplicate_wc_oclc': 1,

            'holdings_out_of_range': 1,
            'holdings_out_of_issn_db_date_range': 1,
            'holdings_have_no_years': 0,

            'invalid_local_issn': 1,
            'issn_mismatch': 1,
            'local_issn_does_not_match_wc_issn_a': 0,
            'local_issn_does_not_match_issn_db': 0,

            'oclc_mismatch': 1,
            'title_mismatch': 1,

            'line_583_error': 1,
            'marc_validation_error': 1,
            'missing_field_852a': 1,
        })
        return disqualifying_issues


class FieldsAndIssuesFinder():
    """
    Class for retrieving the correct fields and issue data while running in bulk/headless mode.

    For record fields will first look to the Validator configuration file for any specific data, then to the bulk data. 
    
    For disqualifying issues it first looks to the bulk data for any specific issues, then to the Validator configuration.

    The idea behind this discrepancy is to always look for specifics first. 
    """

    def __init__(self):
        self.validator_config = ValidatorConfig()
        self.bulk_config = BulkConfig()
        self.use_validator_config = False

    def get_fields_for_individual_file(self, filename):
        """
        Look for appropriate fields from the bulk config when presented with an individual file.
        """
        input_fields = self.validator_config.get_input_fields(filename)
        if input_fields:
            self.use_validator_config = True
            return input_fields
        self.use_validator_config = False
        inst_name = self.get_institution_name_from_filename(filename)

        if inst_name in self.bulk_config.bulk_config_data:
            return self.bulk_config.bulk_config_data[inst_name]['input_fields']
        
        elif inst_name in self.bulk_config.associated_names_map:
            program_name = self.bulk_config.associated_names_map[inst_name]
            return self.bulk_config.bulk_config_data[program_name]['input_fields']


    def get_issues_for_individual_file(self, filename):
        """
        Look for appropriate issues from the bulk config when presented with an individual file.

        If we found the file fields in the Validator config, use the issues from the same place.
        """
        inst_name = self.get_institution_name_from_filename(filename)

        if inst_name in self.bulk_config.bulk_config_data and not self.use_validator_config:
            logging.info('Using disqualifying issues set for {}'.format(inst_name))
            return self.bulk_config.bulk_config_data[inst_name]['disqualifying_issues']
        
        elif inst_name in self.bulk_config.associated_names_map:
            program_name = self.bulk_config.associated_names_map[inst_name]
            logging.info('Using disqualifying issues set for {}'.format(program_name))
            return self.bulk_config.bulk_config_data[program_name]['disqualifying_issues']

        else:
            try:
                return self.validator_config.config_data['disqualifying_issues']
            except KeyError:
                # return defaults if nothing else is set
                logging.warning('No disqualifying issues set. Using defaults.')
                return {}

    def get_institution_name_from_filename(self, filename):
        # in case we're sent a file path
        file_proper =  os.path.split(filename)[-1]
        return file_proper.split('.')[0].lower()
