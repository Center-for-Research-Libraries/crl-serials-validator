import os
from pprint import pprint
import sys
import logging
from termcolor import colored, cprint

from validator_lib.utilities import get_jstor_issns
from validator_lib.print_review_workbook import ReviewWorkbookPrinter
from validator_lib.run_mrk_process import MrkProcessRunner
from validator_lib.run_spreadsheet_tsv_csv_process import SpreadsheetTsvCsvRunner
from validator_lib.get_worldcat_data import WorldCatMarcDataExtractor
from validator_lib.validator_issn_db import ValidatorIssnDb
from validator_lib.process_input_data import InputDataProcessor
from validator_lib.terminal_gui_utilities import print_terminal_page_header


class ChecksRunner:
    def __init__(
        self, input_file, input_fields, disqualifying_issue_categories, data_storage_folder, data_folder, output_dir, 
        issn_db_location, running_headless=False, papr_output=False):

        self.running_headless = running_headless
        self.papr_output = papr_output

        self.output_dir = output_dir

        self.jstor = get_jstor_issns(data_folder)

        self.worldcat_data_getter = WorldCatMarcDataExtractor(data_storage_folder)

        stc_runner = SpreadsheetTsvCsvRunner()
        validator_issn_db = ValidatorIssnDb(issn_db_location)

        found_issn_db = validator_issn_db.issn_db.found_issn_db

        print_terminal_page_header('Processing {}'.format(input_file))
        if input_file.endswith('mrk'):
            mrk_runner = MrkProcessRunner(input_file, input_fields)
            input_file_data, line_583_validation_output = mrk_runner.get_data_from_marc()
        else:
            input_file_data = stc_runner.get_input_data_from_file(input_file, input_fields)
            line_583_validation_output = None
        self.add_worldcat_data_to_input_file_data_dicts(input_file_data, input_file)
        validator_issn_db.process_title_dicts(input_file_data, input_file)

        InputDataProcessor(input_file_data, input_fields, disqualifying_issue_categories, found_issn_db, self.jstor)

        ReviewWorkbookPrinter(input_file_data, line_583_validation_output, self.running_headless, self.papr_output)

    def add_worldcat_data_to_input_file_data_dicts(self, input_file_data, input_file):
        print("Getting {}.".format(colored('WorldCat data', 'cyan')))
        for i in range(0, len(input_file_data)):
            pct_done = colored(str('{0:.1%}'.format(i/len(input_file_data))), 'yellow')
            sys.stdout.write('\r{}'.format(pct_done))
            sys.stdout.flush()
            worldcat_data = self.worldcat_data_getter.get_worldcat_marc_data(input_file_data[i]['local_oclc'])
            # if worldcat_data['wc_title'] == 'Failed title':
            #     cprint('No WorldCat data found for OCLC {}'.format(input_file_data[i]['local_oclc']), 'red')

            for data_cat in worldcat_data:
                input_file_data[i][data_cat] = worldcat_data[data_cat]
        print()
        self.worldcat_data_getter.log_worldcat_data_not_found()
