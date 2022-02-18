from pprint import pprint
import sys
from collections import namedtuple
import logging
from termcolor import colored

from crl_lib.crl_utilities import check_for_valid_issn
from crl_lib.issn_db import IssnDb
from crl_lib.marc_utilities import get_field_subfield
from crl_lib.date_utilities import check_year_between
from crl_lib.marc_fields import MarcFields

from validator_lib.utilities import get_valid_forms, get_valid_serial_types


class ValidatorIssnDb:
    def __init__(self, issn_db_location):

        self.issn_db = IssnDb(issn_db_location=issn_db_location, ignore_missing_db=True)
        self.issn_type_order = ['issn_l', 'issn_z', 'issn_y', 'issn_m']

        self.valid_forms = get_valid_forms()
        self.valid_serial_types = get_valid_serial_types()

    def process_title_dicts(self, title_dicts, input_file):
        logging.debug("Getting ISSN database data for " + input_file)
        if self.issn_db.found_issn_db is False:
            logging.debug("ISSN database does not exist. Skipping.")
            return
        n = 0
        for title_dict in title_dicts:
            n += 1
            if self.issn_db.conn is None:
                self.process_dict_without_issn_db_access(title_dict)
                continue
            pct_done = colored(str('{0:.1%}'.format(n/len(title_dicts))), 'yellow')
            sys.stdout.write('\rISSN db work at {}'.format(pct_done))
            db_data_local = self.get_issn_db_data(title_dict['local_issn'], title_dict['holdings_start'],
                                                  title_dict['holdings_end'])
            db_data_wc = self.get_issn_db_data(title_dict['wc_issn_a'], title_dict['008_year_1'],
                                               title_dict['008_year_2'])
            title_dict['issn_db_issn'] = db_data_local['issn_db_issn']
            title_dict['issn_db_title'] = db_data_local['issn_db_title']
            title_dict['issn_db_format'] = db_data_local['issn_db_format']
            title_dict['issn_db_form_not_print'] = db_data_local['issn_db_form_not_print']
            title_dict['issn_db_serial_type'] = db_data_local['issn_db_serial_type']
            title_dict['issn_db_serial_type_not_periodical'] = db_data_local['issn_db_serial_type_not_periodical']
            title_dict['issn_db_year_1'] = db_data_local['issn_db_year_1']
            title_dict['issn_db_year_2'] = db_data_local['issn_db_year_2']
            title_dict['holdings_out_of_issn_db_date_range'] = db_data_local['holdings_out_of_issn_db_date_range']
            title_dict['local_issn_does_not_match_issn_db'] = db_data_local['issn_mismatch']
            title_dict['wc_issn_does_not_match_issn_db_issn'] = db_data_wc['issn_mismatch']
            if title_dict['local_issn']:
                if check_for_valid_issn(title_dict['local_issn']) is False:
                    title_dict['invalid_issn'] = '1'
        print()

    @staticmethod
    def process_dict_without_issn_db_access(title_dict):
        cats = ['issn_db_issn', 'issn_db_title', 'issn_db_format', 'issn_db_form_not_print', 'issn_db_serial_type',
                'issn_db_serial_type_not_periodical', 'issn_db_year_1', 'issn_db_year_2', 'holdings_out_of_issn_db_date_range',
                'local_issn_does_not_match_issn_db_issn', 'wc_issn_does_not_match_issn_db_issn']
        for cat in cats:
            title_dict[cat] = ''

    def get_issn_db_data(self, issn, year_1, year_2):
        db_data = {
            'issn_db_issn': '',
            'issn_mismatch': '',
            'issn_db_title': '',
            'issn_db_format': '',
            'issn_db_form_not_print': '',
            'issn_db_serial_type': '',
            'issn_db_serial_type_not_periodical': '',
            'issn_db_year_1': '',
            'issn_db_year_2': '',
            'holdings_out_of_issn_db_date_range': ''
        }
        if not issn or str(issn) == 'None':
            return db_data
        issn_data = self.choose_best_issn(issn, year_1, year_2)
        if not issn_data:
            db_data['issn_mismatch'] = '1'
            return db_data

        db_data['issn_db_issn'] = issn_data.issn

        db_data['issn_mismatch'] = ''
        if issn != db_data['issn_db_issn']:
            db_data['issn_mismatch'] = '1'

        db_data['issn_db_title'] = issn_data.title_a

        db_data['issn_db_format'] = issn_data.form
        if issn_data.form in self.valid_forms:
            db_data['issn_db_form_not_print'] = ''
        else:
            db_data['issn_db_form_not_print'] = '1'

        db_data['issn_db_serial_type'] = issn_data.serial_type
        if issn_data.serial_type in self.valid_serial_types:
            db_data['issn_db_serial_type_not_periodical'] = ''
        else:
            db_data['issn_db_serial_type_not_periodical'] = '1'

        db_data['issn_db_year_1'] = issn_data.year_1
        db_data['issn_db_year_2'] = issn_data.year_2

        if not year_1 or not db_data['issn_db_year_1'].isdigit() or not db_data['issn_db_year_2'].isdigit():
            db_data['holdings_out_of_issn_db_date_range'] = ''
        else:
            if not check_year_between(issn_data.year_1, issn_data.year_2, year_1):
                db_data['holdings_out_of_issn_db_date_range'] = '1'
            elif not check_year_between(issn_data.year_1, issn_data.year_2, year_2):
                db_data['holdings_out_of_issn_db_date_range'] = '1'
            else:
                db_data['holdings_out_of_issn_db_date_range'] = ''

        return db_data

    def choose_best_issn(self, issn, year_1, year_2):
        issn_data = self.get_data_from_issn_db(issn)
        if issn_data:
            return issn_data
        issn_marc_dict = self.issn_db.get_marc_from_issn_db_any_issn_type(issn)
        for issn_type in self.issn_type_order:
            for marc in issn_marc_dict[issn_type]:
                issn_data = self._check_valid_issn_marc(marc, year_1, year_2)
                if issn_data:
                    return issn_data
        return None

    def _check_valid_issn_marc(self, marc, year_1, year_2):
        issn_a = get_field_subfield(marc, '022', 'a')
        issn_data = self.get_data_from_issn_db(issn_a)
        if issn_data.form in self.valid_forms:
            if issn_data.serial_type in self.valid_serial_types:
                if self.check_holdings_dates_against_issn_dates(issn_data, year_1, year_2):
                    return issn_data
        return None

    def get_data_from_issn_db(self, issn):
        if issn is None:
            return
        marc = self.issn_db.get_marc_from_issn_a(issn)
        if not marc:
            return

        issn_data_tuple = namedtuple("IssnDbTuple",
                                     "marc issn year_1 year_2 publisher form serial_type bib_lvl title_a title_b")
        mf = MarcFields(marc, log_warnings=True, debug_info='from ISSN database')
        title_a, title_b = self.issn_db.get_titles_from_issn_marc(marc)
        return_data = issn_data_tuple(marc, issn, mf.year_1, mf.year_2, mf.imprint, mf.form, mf.serial_type, mf.bib_lvl, title_a, title_b)
        return return_data

    @staticmethod
    def check_holdings_dates_against_issn_dates(issn_data, year_1, year_2):
        if not year_1 or not year_2:
            return True
        if not check_year_between(issn_data.year_1, issn_data.year_2, year_1):
            return False
        if not check_year_between(issn_data.year_1, issn_data.year_2, year_2):
            return False
        return True
