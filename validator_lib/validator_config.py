import os
import configparser
import yaml
import re
from collections import OrderedDict


class ValidatorConfig:

    config_file = os.path.join(os.getcwd(), 'data', 'config.yaml')

    def __init__(self):
        self.config = {}

        self.issue_categories = self.get_issue_categories()

        self.read_validator_config_file()
        self.check_that_all_issues_are_in_config()

    def read_validator_config_file(self):
        """
        Read the YAML config file. 
        
        First check if it exists and if it is valid YAML. If either of these is false, write a blank file and load that.
        """
        try:
            config = self._read_config()
            if isinstance(config, dict):
                self.config = config
            else:
                self.config = {}
        except FileNotFoundError:
            self.config = {}
        except yaml.io.UnsupportedOperation:
            # means the file there is not a YAML file
            # TODO: this will erase the config file entirely. We should make a failure option, in case
            # the user has (badly) edited the YAML file by hand.
            self.config = {}

        if 'disqualifying_issues' not in self.config:
            disqualifying_issues = self.get_default_disqualifying_issues()
            # YAML can't write an OrderdDict, so convert to dict
            self.config['disqualifying_issues'] = dict(disqualifying_issues)

    def _read_config(self):
        with open(self.config_file, 'r', encoding='utf8') as fin:
            config = yaml.safe_load(fin)
        return config

    def write_validator_config_file(self):
        with open(self.config_file, 'w', encoding='utf8') as fout:
            yaml.safe_dump(self.config, fout)

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
                self.config['disqualifying_issues'][issue] = False
                changed_issues = True
        for issue in self.issue_categories:
            if issue not in default_issues:
                self.config['disqualifying_issues'].pop(issue)
                changed_issues = True
        if changed_issues:
            self.write_validator_config_file()

    def get_issue_categories(self):
        default_issues = self.get_default_disqualifying_issues()
        issue_categories = list(default_issues.keys())
        return issue_categories

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
            'bib_lvl_not_serial': True,
            'form_not_print': True,
            'record_type_not_language_material': True,
            'serial_type_not_periodical': True,
            'invalid_carrier_type': True,
            'invalid_media_type': True,
            'issn_db_form_not_print': True,
            'issn_db_serial_type_not_periodical': True,
            'no_oclc_number': True,
            'no_worldcat_record': True,

            'binding_words_in_holdings': True,
            'completeness_words_in_holdings': True,
            'nonprint_words_in_holdings': True,

            'title_in_jstor': False,

            'duplicate_holdings_id': True,
            'duplicate_local_oclc': True,
            'duplicate_wc_oclc': True,

            'holdings_out_of_range': True,
            'holdings_out_of_issn_db_date_range': True,
            'holdings_have_no_years': False,

            'invalid_local_issn': True,
            'issn_mismatch': True,
            'local_issn_does_not_match_wc_issn_a': False,
            'local_issn_does_not_match_issn_db': False,

            'oclc_mismatch': True,
            'title_mismatch': True,

            'line_583_error': True,
            'marc_validation_error': True,
            'missing_field_852a': True,
        })
        return disqualifying_issues
