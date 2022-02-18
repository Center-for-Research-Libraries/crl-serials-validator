from collections import defaultdict, Counter
import os
from pprint import pprint
import logging
import csv
import re

from crl_lib.crl_xlsxwriter import CRLXlsxWriter
import validator_lib.utilities


class ReviewWorkbookPrinter:
    def __init__(
        self, title_dicts, line_583_validation_output, running_headless, papr_output,
        print_errors_only=False, 
        print_originally_from=False,
        print_issues_worksheets=False,
        print_for_review=False,
        print_good_marc_output=True):

        self.running_headless = running_headless
        self.papr_output = papr_output
        self.print_originally_from = print_originally_from
        self.print_issues_worksheets = print_issues_worksheets
        self.print_for_review = print_for_review
        self.print_good_marc_output = print_good_marc_output

        self.total_records = {}

        # if we have KeyErrors with dict keys containing "issn_db" we'll know the database isn't installed
        self.issn_db_not_seen = False

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
            'ignored_error_category',
            'seqnum',
            'bib_id',
            'holdings_id',
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
            'wc_issn_does_not_match_issn_db_issn',
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

        self.originally_from_header = ['Load Status', 'Reasons for Review', 'HoldingID', 'OCLC Number', 'Print ISSN',
                                       'Title', 'OCLC Symbol', 'OCLC HLC', 'Summary Holdings/Materials Specified']

        self.error_counter = defaultdict(Counter)
        self.disqualifying_error_counter = defaultdict(Counter)
        self.count_errors(title_dicts)
        self.count_disqualifying_errors(title_dicts)
        self.checklist_outputs = defaultdict(list)
        self.error_outputs = defaultdict(list)
        self.get_checklist_data_for_output()

        if self.issn_db_not_seen is True:
            self.remove_issn_db_from_checklist_cats()

        self.output_folder = os.path.join(os.getcwd(), 'output')
        self.error_category_map = self.make_error_category_map()

        self.outputs = {}

        self.make_notes_worksheet()

        for title_dict in self.title_dicts:
            self.organize_by_errors(title_dict)
        if self.print_originally_from is True:
            self.make_originally_from_outputs()

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
            'duplicate_holdings_id': 'Duplicate holdings ID',
            'duplicate_local_oclc': 'Duplicate local OCLC #',
            'duplicate_wc_oclc': 'Duplicate WorldCat OCLC #',
            'form_not_print': 'Form of title is not hard copy',
            'holdings_out_of_issn_db_date_range': 'Holdings are outside the ISSN database expected publication dates',
            'holdings_out_of_range': 'Holdings are outside the expected publication dates',
            'invalid_carrier_type': 'Carrier type of title is not hard copy',
            'invalid_local_issn': 'Local ISSN is not in a valid format',
            'invalid_media_type': 'Media type of title is not hard copy',
            'issn_db_form_not_print': 'ISSN database record has does not have hard copy form',
            'issn_db_serial_type_not_periodical': 'ISSN database record does not have periodical serial type',
            'issn_mismatch': 'ISSN mismatch with WorldCat and ISSN database',
            'local_issn_does_not_match_wc_issn_a': 'Local ISSN mismatch with WorldCat ISSN',
            'local_issn_does_not_match_issn_db': 'Local ISSN mismatch with ISSN database',
            'line_583_error': 'One of more errors in 583 line(s)',
            'local_issn_does_not_match_issn_db': 'ISSN does not match with ISSN database',
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
            inst = self.get_inst_from_dict(title_dict)
            if not title_dict['error_category']:
                self.error_counter[inst]['No errors'] += 1
            else:
                self.error_counter[inst][title_dict['error_category']] += 1

    def count_disqualifying_errors(self, title_dicts):
        """Tally the issues in the input files."""
        for title_dict in title_dicts:
            inst = self.get_inst_from_dict(title_dict)
            try:
                marc = title_dict['marc']
            except KeyError:
                marc = None
            if not title_dict['disqualifying_error_category']:
                self.disqualifying_error_counter[inst]['No errors'] += 1
                if marc:
                    self.good_marc[inst].append(marc)
            else:
                self.disqualifying_error_counter[inst][title_dict['disqualifying_error_category']] += 1
                if marc:
                    self.bad_marc[inst].append(marc)

    def organize_by_errors(self, title_dict):
        inst = self.get_inst_from_dict(title_dict)
        if 'for_review' not in self.outputs[inst]:
            self.outputs[inst]['for_review'] = defaultdict(list)
        if not title_dict['errors']:
            return
        for error_cat in title_dict['errors']:
            try:
                error_str = self.error_category_map[error_cat]
            except:
                raise Exception('Unknown error Validator error category seen. Category is {}'.format(error_cat))
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

    @staticmethod
    def get_inst_from_dict(title_dict):
        if title_dict['institution']:
            return title_dict['institution']
        abbrev = validator_lib.utilities.get_abbrev_from_input_filename(title_dict['filename'])
        return abbrev

    def make_notes_worksheet(self):
        overview_dict = defaultdict(Counter)
        for title_dict in self.title_dicts:
            inst = self.get_inst_from_dict(title_dict)
            overview_dict[inst]['total'] += 1
            if not title_dict['invalid_record'] == '1':
                overview_dict[inst]['no_issues'] += 1
            else:
                overview_dict[inst]['for_review'] += 1
        for inst in overview_dict:
            self.total_records[inst] = overview_dict[inst]['total']
            overview_output = [['{} records'.format(inst), ''],
                               ['Supplied by {}'.format(inst), overview_dict[inst]['total']], ['', ''],
                               ['No issues preventing ingestion', overview_dict[inst]['no_issues']], ['', ''],
                               ['For review', overview_dict[inst]['for_review']]]
            self.outputs[inst] = {'All issues': overview_output}
            if self.print_originally_from is True:
                self.outputs[inst]['originally_from'] = [self.originally_from_header]

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

    def make_originally_from_outputs(self):
        """
        Make workbook listing everything in the original file. By default this is not made or printed, and must be 
        turned on via the print_originally_from variable.
        """
        for title_dict in self.title_dicts:
            inst = self.get_inst_from_dict(title_dict)

            if 'field_852a' not in title_dict:
                title_dict['field_852a'] = title_dict['oclc_symbol']

            load_status = 'review'
            if not title_dict['invalid_record'] == '1' and not title_dict['disqualifying_errors']:
                load_status = 'validated'
            if title_dict['local_title']:
                title = title_dict['local_title']
            else:
                title = title_dict['wc_title']
            output_row = [
                load_status,
                title_dict['error_category'],
                title_dict['holdings_id'],
                title_dict['local_oclc'],
                title_dict['local_issn'],
                title,
                title_dict['field_852a'],
                title_dict['location'],
                title_dict['local_holdings']
            ]
            self.outputs[inst]['originally_from'].append(output_row)

    def check_for_583s_in_files(self):
        seen_insts = set()
        for title_dict in self.title_dicts:
            inst = self.get_inst_from_dict(title_dict)
            if inst in seen_insts:
                continue
            if '583_in_file' in title_dict and title_dict['583_in_file']:
                self.print_line_583_output.add(inst)

    def get_checklist_data_for_output(self):
        insts = set()
        for title_dict in self.title_dicts:
            inst = self.get_inst_from_dict(title_dict)
            insts.add(inst)
            output_list = []
            for cat in self.checklist_cats:
                try:
                    output_list.append(title_dict[cat])
                except KeyError:
                    if 'issn_db' in cat:
                        if self.issn_db_not_seen is False:
                            self.issn_db_not_seen = True
                            logging.info('Skipping output of ISSN db related categories.')
                    else:
                        logging.error('Category {} not seen in checklist data.'.format(cat))
            if self.print_errors_only is True and not output_list[0]:
                continue

            if output_list[0]:
                self.error_outputs[inst].append(output_list)

            self.checklist_outputs[inst].append(output_list)
        if self.issn_db_not_seen is True:
            self.remove_issn_db_from_checklist_cats()
        for inst in insts:
            self.checklist_outputs[inst].insert(0, self.checklist_cats)

    def make_good_bad_marc_output(self, good_or_bad):
        if self.print_good_marc_output is False:
            return
        for inst in self.good_marc:
            output_filename = '{} {} records.mrk'.format(inst, good_or_bad)
            output_file_location = os.path.join(self.output_folder, output_filename)
            output_file_location = validator_lib.utilities.get_unused_filename(output_file_location)

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
            output_file_location = validator_lib.utilities.get_unused_filename(output_file_location)

            for_review_list, for_review_special_rows = self.make_error_worksheet(self.outputs[inst]['for_review'])
            error_count_output = self.make_error_counts_output(inst)
            disqualifying_error_count_output = self.make_disqualifying_error_counts_output(inst)

            for_review_special_formats = [
                ({'bold': True, 'bg_color': '#D8D8D8', 'text_wrap': True}, [0]),
                ({'bold': True, 'bg_color': '#FBE5D6', 'font_size': '14'}, for_review_special_rows)
            ]

            output_pages = {}
            output_pages['Notes'] = {'data': self.outputs[inst]['All issues']}

            checklist_number_columns = {1, 3, 6, 7}  # has_disqualifying_error, seqnum, local_oclc, wc_oclc
            output_pages['Checklist'] = {'data': self.checklist_outputs[inst], 'number_columns': checklist_number_columns}

            if self.total_records[inst] >= 50000:
                error_pages = {}

                error_filename = '{} errors.xlsx'.format(inst)
                error_file_location = os.path.join(self.output_folder, error_filename)
                error_file_location = validator_lib.utilities.get_unused_filename(error_file_location)
                error_pages['Checklist'] = {'data': self.error_outputs[inst], 'number_columns': checklist_number_columns}

                self.error_outputs[inst].insert(0, self.checklist_cats)
                error_pages['All issues'] = {'data': error_count_output, 'special_formats': [({'bold': True, 'text_wrap': True}, [2])]}
                error_pages['Disqualifying issues'] = {'data': disqualifying_error_count_output, 'special_formats': [({'bold': True, 'text_wrap': True}, [2])]}
                error_pages['For review'] = {'data': for_review_list, 'special_formats': for_review_special_formats}

                CRLXlsxWriter(error_file_location, error_pages)

            if self.print_for_review is True:
                output_pages['For review'] = {'data': for_review_list, 'special_formats': for_review_special_formats}
            
            if inst in self.print_line_583_output:
                if self.line_583_validation_output and self.print_errors_only is False:
                    output_pages['Line 583 validation'] = {'data': self.line_583_validation_output}

            if self.running_headless is True:
                self.print_headless_checklist(output_pages['Checklist'], output_file_location.replace('.xlsx', '.txt'))

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
            'MethodofAction_583$i',
            'Status_583$l',
            'PublicNote_583$z',
            'ProgramName_583$f',
            'SiteOfAction_583$j',
            'MaterialsSpecified_583$3',
            'CustodialHistory_561$3a5',
            'ArchivingInstitution_583$5'
        ]
        for record_dict in self.title_dicts:
            inst = self.get_inst_from_dict(record_dict)
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
