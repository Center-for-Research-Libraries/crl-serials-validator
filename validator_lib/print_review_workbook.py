from collections import defaultdict, Counter
import os
from pprint import pprint
import logging
import csv
import re

from crl_lib.crl_xlsxwriter import CRLXlsxWriter

import validator_lib.utilities
from validator_lib import ISSN_DB_LOCATION


class ReviewWorkbookPrinter:
    def __init__(
        self, 
        title_dicts, line_583_validation_output, running_headless, papr_output,
        print_errors_only=False, 
        print_for_review=False,
        print_good_marc_output=True):

        if not ISSN_DB_LOCATION:
            logging.info('Skipping output of ISSN db related categories.')

        self.running_headless = running_headless
        self.papr_output = papr_output
        self.print_for_review = print_for_review
        self.print_good_marc_output = print_good_marc_output

        self.error_rows = defaultdict(list)
        self.total_records = {}

        self.good_marc = defaultdict(list)
        self.bad_marc = defaultdict(list)

        self.title_dicts = title_dicts
        self.print_errors_only = print_errors_only

        self.line_583_validation_output = line_583_validation_output
        self.print_line_583_output = set()
        self.check_for_583s_in_files()

        self.checklist_cats = [
            'disqualifying_error_category',
            'has_disqualifying_error',
            'warning_category',
            'seqnum',
            'bib_id',
            'bib_id_repeated',
            'holdings_id',
            'holdings_id_repeated',
            'local_oclc',
            'wc_oclc',
            'oclc_mismatch',
            'local_oclc_repeated',
            'wc_oclc_repeated',
            'oclcs_019',
            'local_issn',
            'wc_issn_a',
            'local_issn_does_not_match_wc_issn_a',
            'issn_l',
            'local_title',
            'wc_title',
            'title_mismatch',
            'uniform_title',
            'title_h',
            'publisher',
            'form',
            'bib_lvl',
            'serial_type',
            'carrier_type',
            'media_type',
            'place',
            'lang',
            'govt_pub',
            'authentication_code',
            'cat_agent',
            'cat_lang',
            'lc_class',
            'dewey',
            '008_year_1',
            '008_year_2',
            'start_including_362',
            'end_including_362',
            'holdings_start',
            'holdings_end',
            'start_problem',
            'end_problem',
            'holdings_out_of_range',
            'holdings_have_no_years',
            'local_holdings',
            'nonpublic_notes',
            'public_notes',
            'completeness_words_in_holdings',
            'binding_words_in_holdings',
            'nonprint_words_in_holdings',
            'wc_line_362',
            'current_freq',
            'former_freq',
            'preceding_oclcs',
            'succeeding_oclcs',
            'other_oclcs',
            'numbering_peculiarities',
            'title_in_jstor',
            'issn_db_issn',
            'local_issn_does_not_match_issn_db',
            'wc_issn_does_not_match_issn_db',
            'no_issn_matches_issn_db',
            'issn_db_title',
            'issn_db_format',
            'issn_db_serial_type',
            'issn_db_year_1',
            'issn_db_year_2',
            'holdings_out_of_issn_db_date_range'
        ]

        self.for_review_header = ['Record ID',
                                  'Reason for Review',
                                  'Local OCLC#',
                                  'WorldCat OCLC#',
                                  'Local ISSN',
                                  'WorldCat ISSN',
                                  'WorldCat Title',
                                  'MARC Serial Type',
                                  'MARC Form of Item',
                                  'MARC Bib Level',
                                  'Publication Date1',
                                  'Publication Date2',
                                  'Managing Library',
                                  'Location',
                                  'Holdings',
                                  'WorldCat MARC 362'
                                  ]

        self.error_counter = defaultdict(Counter)
        self.disqualifying_error_counter = defaultdict(Counter)
        self.count_errors(title_dicts)
        self.count_disqualifying_errors(title_dicts)
        self.checklist_outputs = defaultdict(list)
        self.error_outputs = defaultdict(list)
        self.get_checklist_data_for_output()

        if not ISSN_DB_LOCATION:
            self.remove_issn_db_from_checklist_cats()

        self.output_folder = os.path.join(os.getcwd(), 'output')
        self.error_category_map = self.make_error_category_map()

        self.outputs = {}

        self.make_notes_worksheet()

        for title_dict in self.title_dicts:
            self.organize_by_errors(title_dict)

        self.make_workbooks()
        
        if self.papr_output is True:
            self.make_good_bad_marc_output('good')
            self.make_good_bad_marc_output('bad')

            self.make_583_output()

    def remove_issn_db_from_checklist_cats(self):
        new_checklist_cats = []
        for cat in self.checklist_cats:
            if 'issn_db' not in cat:
                new_checklist_cats.append(cat)
        self.checklist_cats = new_checklist_cats

    @staticmethod
    def make_error_category_map():
        error_category_map = {
            'bib_lvl_not_serial': 'Bib level of title is not serial',
            'binding_words_in_holdings': 'Binding statements in holdings or notes',
            'completeness_words_in_holdings': 'Completeness or reprint statement in holdings or notes',
            'bib_id_repeated': 'Duplicate bib ID',
            'holdings_id_repeated': 'Duplicate holdings ID',
            'local_oclc_repeated': 'Duplicate local OCLC #',
            'wc_oclc_repeated': 'Duplicate WorldCat OCLC #',
            'form_not_print': 'Form of title is not hard copy',
            'holdings_out_of_issn_db_date_range': 'Holdings are outside the ISSN database expected publication dates',
            'holdings_out_of_range': 'Holdings are outside the expected publication dates',
            'invalid_carrier_type': 'Carrier type of title is not hard copy',
            'invalid_local_issn': 'Local ISSN is not in a valid format',
            'invalid_media_type': 'Media type of title is not hard copy',
            'issn_db_form_not_print': 'ISSN database record has does not have hard copy form',
            'issn_db_serial_type_not_periodical': 'ISSN database record does not have periodical serial type',
            'issn_mismatch': 'ISSN mismatch between WorldCat and ISSN database',
            'local_issn_does_not_match_wc_issn_a': 'Local ISSN mismatch with WorldCat ISSN',
            'local_issn_does_not_match_issn_db': 'Local ISSN mismatch with ISSN database',
            'line_583_error': 'One of more errors in 583 line(s)',
            'no_issn_matches_issn_db': 'Neither local nor WorldCat ISSN matches ISSN database',
            'marc_validation_error': 'MARC record does not validate successfully',
            'missing_field_852a': 'No field 852 $a in MARC input',
            'nonprint_words_in_holdings': 'Nonprint statement in holdings',
            'no_oclc_number': 'No OCLC number in original record',
            'oclc_mismatch': 'OCLC number mismatch with WorldCat',
            'record_type_not_language_material': 'Record type of title is not a language item',
            'serial_type_not_periodical': 'Serial type of title is not periodical',
            'title_mismatch': 'Title mismatch with WorldCat',
            'wc_issn_does_not_match_issn_db': 'WorldCat ISSN does not match with ISSN database',
            'no_worldcat_record': 'Title not found in WorldCat'
        }
        return error_category_map

    def count_errors(self, title_dicts):
        """Tally the issues in the input files."""
        for title_dict in title_dicts:
            inst = title_dict['institution']
            if not title_dict['error_category']:
                self.error_counter[inst]['No errors'] += 1
            else:
                self.error_counter[inst][title_dict['error_category']] += 1

    def count_disqualifying_errors(self, title_dicts):
        """Tally the issues in the input files."""
        for title_dict in title_dicts:
            inst = title_dict['institution']
            try:
                marc = title_dict['marc']
            except KeyError:
                marc = None
            if not title_dict['disqualifying_error_category']:
                self.disqualifying_error_counter[inst]['No errors'] += 1
                if marc:
                    self.good_marc[inst].append(marc)
            else:
                cat = title_dict['disqualifying_error_category']
                self.disqualifying_error_counter[inst][cat] += 1
                if marc:
                    self.bad_marc[inst].append(marc)

    def organize_by_errors(self, title_dict):
        inst = title_dict['institution']
        if 'for_review' not in self.outputs[inst]:
            self.outputs[inst]['for_review'] = defaultdict(list)
        if not title_dict['errors']:
            return
        for error_cat in title_dict['errors']:
            try:
                error_str = self.error_category_map[error_cat]
            except:
                exception_msg = 'Unknown error Validator error category seen. '
                exception_msg += 'Category is {}'.format(error_cat)
                raise Exception(exception_msg)
            output_row = [
                title_dict['record_id'],
                error_str,
                title_dict['local_oclc'],
                title_dict['wc_oclc'],
                title_dict['local_issn'],
                title_dict['wc_issn_a'],
                title_dict['wc_title'],
                title_dict['serial_type'],
                title_dict['form'],
                title_dict['bib_lvl'],
                title_dict['start_including_362'],
                title_dict['end_including_362'],
                inst,
                title_dict['location'],
                title_dict['local_holdings'],
                title_dict['wc_line_362']
            ]
            self.outputs[inst]['for_review'][error_cat].append(output_row)

    def make_notes_worksheet(self):
        overview_dict = defaultdict(Counter)
        for title_dict in self.title_dicts:
            inst = title_dict['institution']
            overview_dict[inst]['total'] += 1
            if not title_dict['invalid_record'] == '1':
                overview_dict[inst]['no_issues'] += 1
            else:
                overview_dict[inst]['for_review'] += 1
        for inst in overview_dict:
            self.total_records[inst] = overview_dict[inst]['total']
            overview_output = [['{} records'.format(inst), ''],
                               ['Supplied by {}'.format(
                                   inst), overview_dict[inst]['total']], ['', ''],
                               ['No issues preventing ingestion', overview_dict[inst]['no_issues']], ['', ''],
                               ['For review', overview_dict[inst]['for_review']]]
            self.outputs[inst] = {'All issues': overview_output}

    def make_error_worksheet(self, inst_data):
        output_list = [self.for_review_header]
        special_rows = []
        for error_cat in inst_data:
            output_list.append([''])
            special_rows.append(len(output_list))
            output_list.append([error_cat])
            for error_line in inst_data[error_cat]:
                output_list.append(error_line)
        return output_list, special_rows

    def make_error_counts_output(self, inst):
        blank_line = ['', '']
        output = [
            [inst, ''],
            blank_line,
            ['errors', 'count']
        ]
        for error_tuple in self.error_counter[inst].most_common():
            output.append(list(error_tuple))
        return output

    def make_disqualifying_error_counts_output(self, inst):
        blank_line = ['', '']
        output = [
            [inst, ''],
            blank_line,
            ['errors', 'count']
        ]
        for disqualifying_error_tuple in self.disqualifying_error_counter[inst].most_common():
            output.append(list(disqualifying_error_tuple))
        return output

    def check_for_583s_in_files(self):
        seen_insts = set()
        for title_dict in self.title_dicts:
            inst = title_dict['institution']
            if inst in seen_insts:
                continue
            if '583_in_file' in title_dict and title_dict['583_in_file']:
                self.print_line_583_output.add(inst)

    def get_checklist_data_for_output(self):
        insts = set()
        row_counts = Counter()
        for title_dict in self.title_dicts:
            inst = title_dict['institution']
            row_counts[inst] += 1
            insts.add(inst)
            output_list = []
            for cat in self.checklist_cats:
                if 'issn_db' in cat and not ISSN_DB_LOCATION:
                    continue
                else:
                    try:
                        output_list.append(title_dict[cat])
                    except KeyError:
                        logging.error(
                            'Category {} not seen in checklist data.'.format(
                                cat))
            if self.print_errors_only is True and not output_list[0]:
                continue
            if output_list[0]:
                self.error_rows[inst].append(row_counts[inst])
                self.error_outputs[inst].append(output_list)
            self.checklist_outputs[inst].append(output_list)
        if not ISSN_DB_LOCATION:
            self.remove_issn_db_from_checklist_cats()
        for inst in insts:
            self.checklist_outputs[inst].insert(0, self.checklist_cats)

    def make_good_bad_marc_output(self, good_or_bad):
        if self.print_good_marc_output is False:
            return
        for inst in self.good_marc:
            output_filename = '{} {} records.mrk'.format(inst, good_or_bad)
            output_file_location = os.path.join(
                self.output_folder, output_filename)
            output_file_location = validator_lib.utilities.get_unused_filename(
                output_file_location)

            with open(output_file_location, 'w', encoding='utf8') as fout:
                if good_or_bad == 'good':
                    for marc in self.good_marc[inst]:
                        fout.write(marc + '\n\n')
                elif good_or_bad == 'bad':
                    for marc in self.bad_marc[inst]:
                        fout.write(marc + '\n\n')

    def make_workbooks(self):
        for inst in self.outputs:
            output_filename = '{} for review.xlsx'.format(inst)
            output_file_location = os.path.join(self.output_folder, output_filename)
            output_file_location = validator_lib.utilities.get_unused_filename(
                output_file_location)

            for_review_list, for_review_special_rows = self.make_error_worksheet(self.outputs[inst]['for_review'])
            error_count_output = self.make_error_counts_output(inst)
            disqualifying_error_count_output = self.make_disqualifying_error_counts_output(inst)

            checklist_special_formats = [
                # ({'bold': True, 'font_color': '#FF0000', 'text_wrap': True}, self.error_rows[inst]),
            ]

            for_review_special_formats = [
                ({'bold': True, 'bg_color': '#D8D8D8', 'text_wrap': True}, [0]),
                ({'bold': True, 'bg_color': '#FBE5D6', 'font_size': '14'}, for_review_special_rows)
            ]

            output_pages = {}
            output_pages['Notes'] = {'data': self.outputs[inst]['All issues']}

            checklist_number_columns = {
                1,   # has_disqualifying_error
                3,   # seqnum
                5,   # bib_id_repeated
                7,   # holdings_id_repeated
                10,  # oclc_mismatch
                11,  # local_oclc_repeated
                12,  # wc_oclc_repeated
                16,  # local_issn_does_not_match_wc_issn_a
                20,  # title_mismatch
                43,  # start_problem
                44,  # end_problem
                45,  # holdings_out_of_range
                46,  # holdings_have_no_years
                50,  # completeness_words_in_holdings
                51,  # binding_words_in_holdings
                52,  # nonprint_words_in_holdings
                60,  # title_in_jstor
                }

            if ISSN_DB_LOCATION:
                checklist_number_columns.add(62)  # local_issn_does_not_match_issn_db
                checklist_number_columns.add(63)  # wc_issn_does_not_match_issn_db
                checklist_number_columns.add(64)  # no_issn_matches_issn_db
                checklist_number_columns.add(70)  # holdings_out_of_issn_db_date_range

            output_pages['Checklist'] = {
                'data': self.checklist_outputs[inst], 
                'number_columns': checklist_number_columns,
                'special_formats': checklist_special_formats
                }

            if self.total_records[inst] >= 50000:
                error_pages = {}

                error_filename = '{} errors.xlsx'.format(inst)
                error_file_location = os.path.join(
                    self.output_folder, error_filename)
                error_file_location = validator_lib.utilities.get_unused_filename(error_file_location)
                error_pages['Checklist'] = {
                    'data': self.error_outputs[inst], 
                    'number_columns': checklist_number_columns
                    }

                self.error_outputs[inst].insert(0, self.checklist_cats)
                error_pages['All issues'] = {
                    'data': error_count_output, 
                    'special_formats': [
                        ({'bold': True, 'text_wrap': True}, [2])]
                    }
                error_pages['Disqualifying issues'] = {
                    'data': disqualifying_error_count_output, 
                    'special_formats': [
                        ({'bold': True, 'text_wrap': True}, [2])]
                    }
                error_pages['For review'] = {
                    'data': for_review_list, 
                    'special_formats': for_review_special_formats
                    }

                CRLXlsxWriter(error_file_location, error_pages)

            if self.print_for_review is True:
                output_pages['For review'] = {
                    'data': for_review_list, 
                    'special_formats': for_review_special_formats
                    }
            
            if inst in self.print_line_583_output:
                if self.line_583_validation_output and self.print_errors_only is False:
                    output_pages['Line 583 validation'] = {
                        'data': self.line_583_validation_output
                        }

            if self.running_headless is True:
                self.print_headless_checklist(
                    output_pages['Checklist'], 
                    output_file_location.replace('.xlsx', '.txt'))

            CRLXlsxWriter(output_file_location, output_pages)
                


    def make_583_output(self):
        if not self.line_583_validation_output:
            return
        output = defaultdict(list)

        header = [
            'Seqnum',
            'Title',
            'Notes',
            'OCLC_Number',
            'Print ISSN',
            'LSN',
            'BibRecNo',
            'Institution Name',
            'InstitutionSymbol_852$a',
            'HoldingLibrary_852$b',
            'CollectionID',
            'ActionNote_583$a',
            'ActionDate_583$c',
            'ExpirationDate_583$d',
            'MethodOfAction_583$i',
            'Status_583$l',
            'PublicNote_583$z',
            'ProgramName_583$f',
            'SiteOfAction_583$j',
            'MaterialsSpecified_583$3',
            'CustodialHistory_561$3a5',
            'ArchivingInstitution_583$5'
        ]
        for record_dict in self.title_dicts:
            inst = record_dict['institution']
            if record_dict['has_disqualifying_error']:
                continue
            for line_583_data in record_dict['lines_583_data']:
                output_row = [
                    record_dict['seqnum'],
                    record_dict['wc_title'],
                    '',  # notes
                    record_dict['wc_oclc'],
                    record_dict['local_issn'],
                    record_dict['holdings_id'],
                    record_dict['bib_id'],
                    inst,
                    record_dict['field_852a'],
                    record_dict['field_852b'],
                    '',  # collection ID
                    line_583_data['a'],
                    line_583_data['c'],
                    line_583_data['d'],
                    line_583_data['i'],
                    line_583_data['l'],
                    line_583_data['z'],
                    line_583_data['f'],
                    line_583_data['j'],
                    line_583_data['3'],
                    record_dict['line_561_as'],
                    record_dict['line_561_3s'],
                    record_dict['line_561_5s']
                ]
                output[inst].append(output_row)

        for inst in output:
            output_filename = '{} for LHRs.txt'.format(inst)
            output_file_location = os.path.join(self.output_folder, output_filename)
            output_file_location = validator_lib.utilities.get_unused_filename(output_file_location)
            with open(output_file_location, 'w', encoding='utf8', newline='') as fout:
                cout = csv.writer(fout, delimiter='\t', lineterminator=os.linesep)
                cout.writerow(header)
                for output_row in output[inst]:
                    cout.writerow(output_row)

    def print_headless_checklist(self, checklist_data, headless_output_filename):
        """
        Special output files for ingest into CRL's PAPR database.
        """
        header_row = checklist_data['data'][0]
        good_output = []
        bad_output = []
        for row in checklist_data['data']:
            if row[1] != '1':
                good_output.append(row)
            else:
                bad_output.append(row)
        
        if good_output:
            good_headless_output_filename = headless_output_filename.replace('review', 'loading')
            fout_good = open(good_headless_output_filename, 'w', encoding='utf8', newline='')
            cout_good = csv.writer(fout_good, delimiter='\t', lineterminator=os.linesep)
            cout_good.writerow(header_row)
            for row in good_output:
                cout_good.writerow(row)
        if bad_output:
            bad_headless_output_filename = headless_output_filename.replace('for review', 'failed')
            fout_bad = open(bad_headless_output_filename, 'w', encoding='utf8', newline='')
            cout_bad = csv.writer(fout_bad, delimiter='\t', lineterminator=os.linesep)
            cout_bad.writerow(header_row)
            for row in bad_output:
                cout_bad.writerow(row)
