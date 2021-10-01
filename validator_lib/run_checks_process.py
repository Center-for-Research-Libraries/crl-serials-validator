import os
from pprint import pprint
import sys
import logging

from validator_lib.utilities import get_jstor_issns
from validator_lib.print_review_workbook import ReviewWorkbookPrinter
from validator_lib.run_mrk_process import MrkProcessRunner
from validator_lib.run_spreadsheet_tsv_csv_process import SpreadsheetTsvCsvRunner
from validator_lib.get_worldcat_data import WorldCatMarcDataExtractor
from validator_lib.validator_issn_db import ValidatorIssnDb
from validator_lib.process_input_data import InputDataProcessor


class ChecksRunner:
    def __init__(
        self, data_storage_folder, data_folder, input_files, output_dir, issn_db_location, 
        files_without_input_fields, running_headless=False):

        self.running_headless = running_headless

        self.output_dir = output_dir
        self.clear_output_folder()

        self.jstor = get_jstor_issns(data_folder)

        self.worldcat_data_getter = WorldCatMarcDataExtractor(data_storage_folder)

        stc_runner = SpreadsheetTsvCsvRunner()
        validator_issn_db = ValidatorIssnDb(issn_db_location)

        found_issn_db = validator_issn_db.issn_db.found_issn_db

        completed_files = set()
        for input_file in input_files:
            if input_file in completed_files:
                continue
            elif input_file in files_without_input_fields:
                print('Skipping {}; no input fields set.'.format(input_file))
                continue
            print('Processing {}'.format(input_file))
            completed_files.add(input_file)
            if input_file.endswith('mrk'):
                mrk_runner = MrkProcessRunner(input_file)
                input_file_data, line_583_validation_output = mrk_runner.get_data_from_marc()
            else:
                input_file_data = stc_runner.get_input_data_from_file(input_file)
                line_583_validation_output = None
            self.add_worldcat_data_to_input_file_data_dicts(input_file_data, input_file)
            validator_issn_db.process_title_dicts(input_file_data, input_file)
            InputDataProcessor(input_file_data, input_file, found_issn_db, self.jstor, input_file)

            ReviewWorkbookPrinter(input_file_data, line_583_validation_output, self.running_headless)

    def add_worldcat_data_to_input_file_data_dicts(self, input_file_data, input_file):
        print("Getting WorldCat data for records in {}.".format(input_file))
        for i in range(0, len(input_file_data)):
            sys.stdout.write('\r{0:.1%}'.format(i/len(input_file_data)))
            sys.stdout.flush()
            worldcat_data = self.worldcat_data_getter.get_worldcat_marc_data(input_file_data[i]['local_oclc'])
            if worldcat_data['wc_title'] == 'Failed title':
                print('No WorldCat data found for OCLC {}'.format(input_file_data[i]['local_oclc']))

            for data_cat in worldcat_data:
                input_file_data[i][data_cat] = worldcat_data[data_cat]
        sys.stdout.write('\r')
        sys.stdout.flush()
        self.worldcat_data_getter.log_worldcat_data_not_found()

    def clear_output_folder(self):
        if self.running_headless is not True:
            while True:
                print('------------')
                print('Should we erase all files in the output folder? (Y/N)')
                clear_question = input()
                if clear_question.lower().startswith('n'):
                    return
                elif clear_question.lower().startswith('y'):
                    break
                else:
                    print("I didn't understand that.\n")
        output_files = os.listdir(self.output_dir)
        for output_file in output_files:
            logging.info('Clearing output folder; deleting {}'.format(output_file))
            output_file_loc = os.path.join(self.output_dir, output_file)
            if not os.path.isfile(output_file_loc):
                continue
            try:
                os.remove(output_file_loc)
            except PermissionError:
                logging.warning("Could not delete file {} due to permissions error".format(output_file))
