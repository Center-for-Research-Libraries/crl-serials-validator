from collections import Counter
from unidecode import unidecode
from pprint import pprint
import logging
import warnings


with warnings.catch_warnings():
    """
    thefuzz on import will often throw the following warning: "Using slow pure-
    python SequenceMatcher. Install python-Levenshtein to remove this warning"

    On Windows installing this requires installing Visual C++ 2019 and so isn't 
    realistic for this project. Instead we'll just suppress the warning.
    """
    warnings.simplefilter("ignore")
    from thefuzz import fuzz


from crl_lib.crl_utilities import check_for_valid_issn
from crl_lib.date_utilities import check_year_between
from crl_lib.validation_utilities import check_for_print_carrier_type, check_for_print_media_type

import validator_lib.utilities
from validator_lib import ISSN_DB_LOCATION


class InputDataProcessor:

    marc_issues_to_check = [
        'line_583_error', 'marc_validation_error', 'missing_field_852a']

    def __init__(
        self, title_dicts, input_fields, disqualifying_issue_categories, 
        jstor_titles
        ):

        self.jstor_titles = jstor_titles
        self.title_dicts = title_dicts
        self.input_fields = input_fields
        self.disqualifying_issue_categories = disqualifying_issue_categories
        self.errors = []
        self.issues_to_check = self.get_issues_to_check()

        self.valid_forms = validator_lib.utilities.get_valid_forms()
        self.valid_serial_types = validator_lib.utilities.get_valid_serial_types()

        self.duplication_check = {}
        self.unique_fields = ['local_oclc', 'wc_oclc', 'holdings_id', 'bib_id']
        self.check_for_duplicated_fields()

        for title_dict in self.title_dicts:
            self.remove_none_strings_from_title_dict(title_dict)
            self.run_unique_checks_on_title(title_dict)
            self.check_for_missing_fields(title_dict)
            self.select_record_id(title_dict)
            self.compare_oclcs(title_dict)
            self.check_issns(title_dict)
            self.match_titles(title_dict)
            self.run_holdings_checks(title_dict)
            self.check_record_type(title_dict)
            self.check_bib_lvl(title_dict)
            self.check_type_of_continuing_resource(title_dict)
            self.check_form(title_dict)
            self.check_carrier_type(title_dict)
            self.check_media_type(title_dict)
            self.check_if_title_in_jstor(title_dict)
            self.assemble_errors_in_dict(title_dict)

    def get_institution(self, title_dict):
        if not title_dict['institution']:
            if title_dict['field_852a']:
                title_dict['institution'] = title_dict['field_852a']
            else:
                title_dict['institution'] = validator_lib.utilities.get_abbrev_from_input_filename(title_dict['filename'])

    def get_issues_to_check(self):
        issues_to_check = [
            'bib_lvl_not_serial', 'binding_words_in_holdings', 'completeness_words_in_holdings', 'form_not_print', 
            'holdings_out_of_range',
            'invalid_carrier_type', 'invalid_local_issn', 'invalid_media_type', 'issn_mismatch', 
            'nonprint_words_in_holdings', 'oclc_mismatch', 'record_type_not_language_material', 
            'serial_type_not_periodical', 'title_mismatch', 'title_in_jstor' ]

        if ISSN_DB_LOCATION:
            issn_db_issues = [
                'holdings_out_of_issn_db_date_range',
                'issn_db_form_not_print', 'issn_db_serial_type_not_periodical', 
                'local_issn_does_not_match_issn_db', 
                'local_issn_does_not_match_wc_issn_a']
            issues_to_check.extend(issn_db_issues)
        return issues_to_check

    def assemble_errors_in_dict(self, title_dict):
        """
        This runs after all other input processing. Basically creates an error 
        list for the outputs
        """
        # Without OCLC in original we can't do anything, so immediately fail
        if not title_dict['local_oclc']:
            title_dict['errors'] = ['no_oclc_number']
            title_dict['disqualifying_errors'] = ['no_oclc_number']
            title_dict['invalid_record'] = '1'
        # Without OCLC a WorldCat record can't do anything, so immediately fail
        elif not title_dict['wc_oclc']:
            title_dict['errors'] = ['no_worldcat_record']
            title_dict['disqualifying_errors'] = ['no_worldcat_record']
            title_dict['invalid_record'] = '1'
        else:
            for issue_to_check in self.issues_to_check:
                if title_dict[issue_to_check] == '1':
                    title_dict['errors'].append(issue_to_check)
                    if issue_to_check in self.disqualifying_issue_categories:
                        title_dict['invalid_record'] = '1'
                        title_dict['disqualifying_errors'].append(
                            issue_to_check)

        # MARC-only errors
        for marc_issue in self.marc_issues_to_check:
            if marc_issue in title_dict['errors'] and marc_issue in self.disqualifying_issue_categories:
                title_dict['invalid_record'] = '1'
                title_dict['disqualifying_errors'].append(marc_issue)
        title_dict['error_category'] = '; '.join(title_dict['errors'])
        title_dict['warnings'] = title_dict['errors'].copy()
        for disqualifying_error in title_dict['disqualifying_errors']:
            try:
                title_dict['warnings'].remove(disqualifying_error)
            except ValueError:
                pass
        title_dict['warning_category'] = '; '.join(title_dict['warnings'])
        title_dict['disqualifying_error_category'] = '; '.join(title_dict['disqualifying_errors'])
        title_dict['has_disqualifying_error'] = ''
        if title_dict['disqualifying_error_category']:
            title_dict['has_disqualifying_error'] = '1'

    def remove_none_strings_from_title_dict(self, title_dict):
        """
        Validator outputs 'None' if there's a blank field. Remove these 
        everywhere, except in titles.
        """
        for cat in title_dict:
            if cat == 'local_title':
                continue
            if type(title_dict[cat]) is str:
                if title_dict[cat].lower() == 'none':
                    title_dict[cat] = ''

    def check_for_duplicated_fields(self):
        for title_dict in self.title_dicts:
            self.get_institution(title_dict)
            for cat in self.unique_fields:
                if not title_dict[cat]:
                    continue
                institution = title_dict['institution']
                location = title_dict['location']
                self.duplication_check.setdefault(institution, {})
                self.duplication_check[institution].setdefault(location, {})
                self.duplication_check[institution][location].setdefault(cat, Counter())
                self.duplication_check[institution][location][cat][title_dict[cat]] += 1

    def run_unique_checks_on_title(self, title_dict):
        institution = title_dict['institution']
        location = title_dict['location']
        for cat in self.unique_fields:
            if not title_dict[cat]:
                continue
            if self.duplication_check[institution][location][cat][title_dict[cat]] > 1:
                title_dict['{}_repeated'.format(cat)] = '1'
                title_dict['errors'].append('{}_repeated'.format(cat))

    def check_for_missing_fields(self, title_dict):
        title_dict['missing_fields'] = ''
        check_fields = ['bib_id', 'holdings_id', 'local_oclc', 'local_holdings']
        for field in check_fields:
            if field in self.input_fields and not title_dict[field]:
                title_dict['missing_fields'] = '1'
                self.errors.append('{}_missing'.format(field))

    @staticmethod
    def select_record_id(title_dict):
        if title_dict['holdings_id']:
            title_dict['record_id'] = title_dict['holdings_id']
        elif title_dict['bib_id']:
            title_dict['record_id'] = title_dict['bib_id']
        else:
            title_dict['record_id'] = ''

    @staticmethod
    def compare_oclcs(title_dict):
        if title_dict['local_oclc']:
            if str(title_dict['local_oclc']) == str(title_dict['wc_oclc']):
                title_dict['oclc_mismatch'] = ''
            else:
                title_dict['oclc_mismatch'] = '1'
        else:
            title_dict['oclc_mismatch'] = ''

    def check_issns(self, title_dict):
        """
        Check for local ISSN that fits he ISSN algorithm.

        issn_mismatch will be considered as false if the local ISSN matches the 
        WorldCat ISSN *or* the ISSN database ISSN.
        """
        if title_dict['local_issn']:
            if check_for_valid_issn(title_dict['local_issn']) is False:
                title_dict['invalid_local_issn'] = '1'

        if title_dict['wc_issn_a']:
            if check_for_valid_issn(title_dict['wc_issn_a']) is False:
                title_dict['invalid_wc_issn_a'] = '1'

        if title_dict['local_issn'] != title_dict['wc_issn_a']:
            title_dict['local_issn_does_not_match_wc_issn_a'] = '1'

    def check_if_title_in_jstor(self, title_dict):
        title_dict['title_in_jstor'] = ''
        issn_cats = ['local_issn', 'wc_issn_a', 'issn_db_issn']
        for issn_cat in issn_cats:
            if issn_cat in title_dict and title_dict[issn_cat]:
                if title_dict[issn_cat] in self.jstor_titles:
                    title_dict['title_in_jstor'] = '1'

    @staticmethod
    def run_holdings_checks(title_dict):
        # "Magic words" in holdings and notes
        title_dict['completeness_words_in_holdings'] = validator_lib.utilities.check_holdings_data_for_magic_words(
            title_dict['local_holdings'], title_dict['nonpublic_notes'], title_dict['public_notes'], 'completeness')

        title_dict['binding_words_in_holdings'] = validator_lib.utilities.check_holdings_data_for_magic_words(
            title_dict['local_holdings'], title_dict['nonpublic_notes'], title_dict['public_notes'], 'binding')
        title_dict['nonprint_words_in_holdings'] = validator_lib.utilities.check_holdings_data_for_magic_words(
            title_dict['local_holdings'], title_dict['nonpublic_notes'], title_dict['public_notes'], 'nonprint')

        if title_dict['holdings_start']:
            start_between = check_year_between(title_dict['start_including_362'], title_dict['end_including_362'],
                                               title_dict['holdings_start'])
            end_between = check_year_between(title_dict['start_including_362'], title_dict['end_including_362'],
                                             title_dict['holdings_end'])
            if start_between is False:
                if '/' in title_dict['wc_line_362'] or '/' in title_dict['local_holdings']:
                    start_between = validator_lib.utilities.double_check_slash_start_year(title_dict['start_including_362'],
                                                                                     title_dict['wc_line_362'],
                                                                                     title_dict['holdings_start'],
                                                                                     title_dict['local_holdings'])
            if end_between is False:
                if '/' in title_dict['wc_line_362'] or '/' in title_dict['local_holdings']:
                    end_between = validator_lib.utilities.double_check_slash_end_year(title_dict['start_including_362'],
                                                                                 title_dict['wc_line_362'],
                                                                                 title_dict['holdings_start'],
                                                                                 title_dict['local_holdings'])
            if start_between is True:
                title_dict['start_problem'] = ''
            elif start_between is False:
                title_dict['start_problem'] = '1'
                title_dict['holdings_out_of_range'] = '1'
            if end_between is True:
                title_dict['end_problem'] = ''
            elif end_between is False:
                title_dict['end_problem'] = '1'
                title_dict['holdings_out_of_range'] = '1'

    @staticmethod
    def check_record_type(title_dict):
        """Language material only"""
        if title_dict['record_type'] and title_dict['record_type'] == 'a':
            title_dict['record_type_not_language_material'] = ''
        else:
            title_dict['record_type_not_language_material'] = '1'

    @staticmethod
    def check_bib_lvl(title_dict):
        """Serial only"""
        if title_dict['bib_lvl'] and title_dict['bib_lvl'] == "s":
            title_dict['bib_lvl_not_serial'] = ''
        else:
            title_dict['bib_lvl_not_serial'] = '1'

    def check_type_of_continuing_resource(self, title_dict):
        """Strict serial check."""
        if title_dict['serial_type'] and title_dict['serial_type'] in self.valid_serial_types:
            title_dict['serial_type_not_periodical'] = ''
        else:
            title_dict['serial_type_not_periodical'] = '1'

    def check_form(self, title_dict):
        """No attempt or regular print repro"""
        if title_dict['form'] and title_dict['form'] in self.valid_forms:
            title_dict['form_not_print'] = ''
        else:
            title_dict['form_not_print'] = '1'

    @staticmethod
    def check_carrier_type(title_dict):
        if not title_dict['carrier_type']:
            title_dict['invalid_carrier_type'] = ''
        elif check_for_print_carrier_type(title_dict['carrier_type']):
            title_dict['invalid_carrier_type'] = ''
        else:
            title_dict['invalid_carrier_type'] = '1'

    @staticmethod
    def check_media_type(title_dict):
        if not title_dict['media_type']:
            title_dict['invalid_media_type'] = ''
        elif check_for_print_media_type(title_dict['media_type']):
            title_dict['invalid_media_type'] = ''
        else:
            title_dict['invalid_media_type'] = ''

    @staticmethod
    def match_titles(title_dict):
        """
        At the moment we're doing simple Levenshtein distances with thefuzz. The 
        numbers probably need to be massaged a lot.
        """
        if not title_dict['local_title'] or not title_dict['wc_title']:
            title_dict['title_mismatch'] = ''
            return
        local_title = unidecode(title_dict['local_title']).lower()
        wc_title = unidecode(title_dict['wc_title']).lower()
        ratio = fuzz.ratio(local_title, wc_title)
        if ratio >= 90:
            title_dict['title_mismatch'] = ''
        else:
            ratio_partial = fuzz.partial_ratio(local_title, wc_title)
            if ratio_partial >= 90:
                title_dict['title_mismatch'] = ''
            else:
                title_dict['title_mismatch'] = '1'
