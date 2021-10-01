import csv
import os
import openpyxl
from collections import Counter
import sys
from pprint import pprint
import logging

from validator_lib.validator_config import FieldsAndIssuesFinder
from validator_lib.utilities import get_first_last_year_from_regular_holdings
from validator_lib.supplements_and_indexes_functions import remove_indexes_from_holdings, remove_supplements_from_holdings


class SpreadsheetTsvCsvRunner:

    string_only_cats = {
            'title', 'issn', 'institution', 'oclc_symbol', 'location', 'holdings_0', 'holdings_1', 'holdings_2', 
            'holdings_3'
            }

    def __init__(self):

        self.fields_and_issues_finder = FieldsAndIssuesFinder()
        self.input_cats = ['holdings_id', 'bib_id', 'oclc', 'issn', 'title', 'institution', 'oclc_symbol', 'location', 
                           'holdings_0', 'holdings_1', 'holdings_2', 'holdings_3']

        self.input_folder = os.path.join(os.getcwd(), 'input')

    def get_row_locations(self, input_fields):
        row_locations = {}
        for cat in self.input_cats:
            if cat in input_fields and input_fields[cat]:
                row_locations[cat] = int(input_fields[cat]) - 1
        row_locations['header_to_skip'] = False
        if 'header' in input_fields:
            row_locations['header_to_skip'] = True
        return row_locations

    def get_input_data_from_file(self, input_file):
        input_fields = self.fields_and_issues_finder.get_fields_for_individual_file(input_file)
        input_file_location = os.path.join(self.input_folder, input_file)
        if input_file.endswith('xlsx'):
            wb = openpyxl.load_workbook(input_file_location)
            iterator = wb.active
        else:
            if input_file.endswith('csv'):
                delimiter = ','
            elif input_file.endswith('txt') or input_file.endswith('tsv'):
                delimiter = '\t'
            else:
                raise Exception('Invalid input file?\n{}'.format(input_file))
            fin = open(input_file_location, 'r', newline='')
            iterator = csv.reader(fin, delimiter=delimiter)

        input_data = self.extract_data_from_spreadsheet_file(iterator, input_file, input_fields)
        return input_data

    def extract_data_from_spreadsheet_file(self, iterator, input_file, input_fields):
        print('Extracting data from {}'.format(input_file))
        row_locations = self.get_row_locations(input_fields)
        input_data = []
        n = 0
        c = Counter()
        for row in iterator:
            if row_locations['header_to_skip'] is True:
                row_locations['header_to_skip'] = False
                continue
            n += 1
            sys.stdout.write('\rReading row {}'.format(n))
            sys.stdout.flush()
            row_dict = {'filename': input_file}
            holdings_list = []
            regular_holdings = []
            for cat in self.input_cats:
                if cat in row_locations:
                    if input_file.endswith('xlsx'):
                        cat_data = row[row_locations[cat]].value
                    else:
                        cat_data = row[row_locations[cat]]
                else:
                    cat_data = ''
                if cat in self.string_only_cats:
                    cat_data = str(cat_data)
                    # common error in spreadsheets
                    if 'VLOOKUP' in cat_data:
                        cat_data = ''
                if 'holdings_' in cat and cat != 'holdings_id' and cat_data:
                    holdings_list.append(str(cat_data))
                    regular_holdings_str, _, _ = remove_supplements_from_holdings(str(cat_data))
                    regular_holdings_str, _, _ = remove_indexes_from_holdings(regular_holdings_str)
                    regular_holdings.append(regular_holdings_str)
                else:
                    if cat in {'oclc', 'issn', 'title'}:
                        dict_cat = 'local_' + cat
                        row_dict[dict_cat] = cat_data
                    else:
                        row_dict[cat] = cat_data                

            c[row_dict['institution']] += 1
            row_dict['seqnum'] = c[row_dict['institution']]
            row_dict['errors'] = []

            row_dict['local_holdings'] = '; '.join(holdings_list)
            holdings_start, holdings_end = get_first_last_year_from_regular_holdings(regular_holdings)
            if holdings_start:
                row_dict['holdings_start'] = int(holdings_start)
                row_dict['holdings_end'] = int(holdings_end)
                row_dict['holdings_have_no_years'] = ''
            else:
                row_dict['holdings_start'] = ''
                row_dict['holdings_end'] = ''
                row_dict['holdings_have_no_years'] = '1'

            row_dict['nonpublic_notes'] = ''
            row_dict['public_notes'] = ''
            self.null_remover(row_dict)
            input_data.append(row_dict)
        print('Finished loading {}'.format(input_file))
        return input_data

    @staticmethod
    def null_remover(row_dict):
        """
        Remove the occasional Excel/Access artifact "Null" in place of blanks.
        """
        for cat in row_dict:
            if str(row_dict[cat]).lower() == 'null':
                row_dict[cat] = ''
