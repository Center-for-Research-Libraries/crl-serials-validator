"""
Runs through any files in the input directory and attempts to make a little sense of them.

For MARC files, records:
    * number of records
    * number with 001
    * number with obvious OCLC 035
    * number with other 035
    * number with 863/864/865
    * number with 866/867/868

At the moment, this doesn't attempt to scan txt/tsv/csv/xlsx files.
"""
import os
import csv
from collections import Counter
import logging
from termcolor import cprint, colored

from crl_lib.marc_file_reader import MarcFileReader
from crl_lib.marc_fields import MarcFields
from crl_lib.terminal_gui_utilities import print_terminal_page_header


class InputFileScanner:
    def __init__(self, input_files):
        
        self.data = {}
        self.input_dir = os.path.join(os.getcwd(), 'input')
        self.input_files = input_files
        self.cats = [
            "Total records", "Have 001 field", "Have 004 field", "Have 035", "OCLC in 035", "Have 583", 
            "Have 863/864/865", "Have 866/867/868"]

    def scan_input_files(self):
        logging.debug("Scanning input files.")
        for input_file in self.input_files:
            if input_file.endswith(".mrk"):
                logging.debug("Scanning {}".format(input_file))
                self.marc_scanner(input_file)
               
            elif input_file.endswith(".xlsx"):
                logging.info("Skipping {}".format(input_file))
            elif input_file.endswith(".txt") or input_file.endswith(".tsv") or input_file.endswith(".csv"):
                logging.info("Skipping {}".format(input_file))
            else:
                logging.warning("Unkown file type in input directory: {}".format(input_file))

    def marc_scanner(self, input_file):
        input_file_loc = os.path.join(self.input_dir, input_file)
        file_data = Counter()
        mfr = MarcFileReader(input_file_loc)
        for marc in mfr:
            file_data["Total records"] += 1
            mf = MarcFields(marc)
            if "=001  " in marc:
                file_data["Have 001 field"] += 1
            if "004  " in marc:
                file_data["Have 004 field"] += 1
            if mf.oclc_035:
                file_data["Have 035"] += 1
                file_data["OCLC in 035"] += 1
            elif "=035  " in marc:
                file_data["Have 035"] += 1
            if "=583  " in marc:
                file_data["Have 583"] += 1
            if "=863  " in marc or "=864  " in marc or "=865  " in marc:
                file_data["Have 863/864/865"] += 1
            if "=866  " in marc or "=867  " in marc or "=868  " in marc:
                file_data["Have 866/867/868"] += 1

        # skip blank file
        if file_data["Total records"] == 0:
            logging.warning('No records found in {}. Blank file?'.format(input_file))
            return
        
        self.print_file_scan_results(input_file, file_data)

    def print_file_scan_results(self, input_file, file_data):
        logging.info('Quick scan of file {}'.format(input_file))
        print_terminal_page_header('Quick scan of file {}'.format(input_file))
        for cat in self.cats:
            output = [cat, file_data[cat], "{:.1%}".format(file_data[cat]/file_data["Total records"])]
            output_string = '{}{}\t{}'.format(
                colored(str(output[0]).ljust(20), 'yellow'), 
                colored(str(output[1]).rjust(5), 'cyan'),
                colored(str(output[2]).rjust(7), 'blue')
            )
            logging.info(output_string)
            print(output_string)

    def text_scanner(self, input_file):
        # TODO:
        input_file_loc = os.path.join(self.input_dir, input_file)
        if input_file.endswith('.csv'):
            delimiter = ','
        else:
            delimiter = '\t'

        file_data = Counter()
        with open(input_file_loc, "r") as fin:
            cin = csv.reader(fin, delimiter=delimiter)
            for row in cin:
                pass
        return file_data

    def xlsx_scanner(self, input_file):
        # TODO:
        file_data = Counter()
        return file_data
