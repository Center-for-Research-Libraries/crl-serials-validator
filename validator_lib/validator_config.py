import os
import configparser
import re
from collections import OrderedDict


class ValidatorConfig:
    def __init__(self):
        self.config = configparser.SafeConfigParser()
        data_folder = os.path.join(os.getcwd(), 'data')
        self.project_config_file = os.path.join(data_folder, 'validator_config.ini')
        self.config_data = {}
        self.read_validator_config_file()

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
