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
from termcolor import colored, cprint

from crl_lib.marc_file_reader import MarcFileReader
from crl_lib.marc_fields import MarcFields


class InputFileScanner:
    def __init__(self, input_files):
        
        self.data = {}
        self.input_dir = os.path.join(os.getcwd(), 'input')
        logging.debug("Scanning input files.")
        for input_file in input_files:
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
            file_data['total'] += 1
            mf = MarcFields(marc)
            if "=001  " in marc:
                file_data['001'] += 1
            if "004  " in marc:
                file_data['004'] += 1
            if mf.oclc_035:
                file_data['035'] += 1
                file_data['oclc_035'] += 1
            elif "=035  " in marc:
                file_data['035'] += 1
            if "=583  " in marc:
                file_data['583'] += 1
            if "=863  " in marc or "=864  " in marc or "=865  " in marc:
                file_data['863'] += 1
            if "=866  " in marc or "=867  " in marc or "=868  " in marc:
                file_data['866'] += 1

        label_color = 'green'
        cat_labels = {
            'total': colored('Total records   ', label_color),
            '001': 'Have {} field  '.format(colored('001', label_color)),
            '004': 'Have {} field  '.format(colored('004', label_color)),
            '035': 'Have {} field  '.format(colored('035', label_color)),
            'oclc_035': '{} in 035     '.format(colored('OCLC', label_color)),
            '583': 'Have {}        '.format(colored('583', label_color)),
            '863': 'Have {}/{}/{}'.format(colored('863', label_color), colored('864', label_color), colored('865', label_color)),
            '866': 'Have {}/{}/{}'.format(colored('866', label_color), colored('867', label_color), colored('868', label_color)),
        }

        cats = ['001', '004', '035', 'oclc_035', '583', '863', '866', 'total']

        # skip blank file
        if file_data['total'] == 0:
            logging.warning('No records found in {}. Blank file?'.format(input_file))
            return
        
        logging.info('Quick scan of file {}'.format(input_file))
        scan_notice_bar = '-------------------'
        for _ in input_file:
            scan_notice_bar = scan_notice_bar + '-'
        print('\nQuick scan of file {}'.format(colored(input_file, 'cyan')))
        cprint(scan_notice_bar, 'blue')
        for cat in cats:
            cat_label = cat_labels[cat]
            if cat == 'total':
                output_pct = ''
            else:
                output_pct = '{:.1%}'.format(file_data[cat]/file_data['total'])
            output_string = '{}{}{}'.format(cat_label.ljust(12), str(file_data[cat]).rjust(8), output_pct.rjust(10))
            logging.info(output_string)
            print(output_string)
        return file_data

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
