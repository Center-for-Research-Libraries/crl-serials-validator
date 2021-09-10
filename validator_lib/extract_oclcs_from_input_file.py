import csv
import os
import re
import openpyxl
import logging

from crl_lib.crl_utilities import clean_oclc
from crl_lib.marc_utilities import get_fields_subfields
from crl_lib.marc_file_reader import MarcFileReader
from crl_lib.marc_fields import MarcFields
from crl_lib.local_marc_db import LocalMarcDb
from validator_lib.validator_config import ValidatorConfig
from validator_lib.utilities import left_pad_field_number, get_input_files, get_file_location_dict, get_failed_oclcs


def choose_oclc_from_multiple_locations(locs):
    if not locs:
        return None
    if len(locs) == 1:
        return locs[0]
    for loc in locs:
        if 'ocm' in loc or 'ocn' in loc or 'oclc' in loc.lower() or 'ocolc' in loc.lower():
            return loc
    # nothing obvious seen, return the first seen field
    return locs[0]


def get_single_oclc(oclc):
    oclc = oclc.replace(',', ';')
    oclc_list = oclc.split(';')
    return oclc_list[0]


def read_marc_data(oclcs, input_file_location, oclc_location):
    mfr = MarcFileReader(input_file_location)
    for record in mfr:
        if oclc_location == '035' or oclc_location == '035a':
            mf = MarcFields(record)
            oclc = mf.oclc_035
            if oclc:
                add_oclc_to_oclcs_set(oclc, oclcs)
        else:
            oclc_locations = get_fields_subfields(record, oclc_location)
            oclc = choose_oclc_from_multiple_locations(oclc_locations)
            add_oclc_to_oclcs_set(oclc, oclcs)


def read_text_data(oclcs, input_file_location, oclc_location, has_header):
    row_index = int(oclc_location) - 1
    delimiter = '\t'
    if input_file_location.endswith('.csv'):
        delimiter = ','
    fin = open(input_file_location, "r")
    # skip header line
    if has_header:
        fin.readline()
    cin = csv.reader(fin, delimiter=delimiter)
    for row in cin:
        try:
            oclc = row[row_index]
        except IndexError:
            continue
        oclc = clean_oclc(oclc)
        add_oclc_to_oclcs_set(oclc, oclcs)


def read_spreadsheet_data(oclcs, input_file_location, oclc_location, has_header_row):
    # TODO
    logging.info('Reading OCLCs from {}'.format(input_file_location))
    oclc_column = int(oclc_location) - 1
    wb = openpyxl.load_workbook(input_file_location)
    ws = wb.active
    line_no = 0
    for row in ws:
        line_no += 1
        if line_no == 1 and has_header_row:
            continue
        oclc = row[oclc_column].value
        add_oclc_to_oclcs_set(oclc, oclcs)


def add_oclc_to_oclcs_set(oclc, oclcs):
    cleaned_oclc = clean_oclc(oclc)
    if cleaned_oclc:
        oclcs.add(cleaned_oclc)


def get_needed_oclcs():
    validator_config = ValidatorConfig()
    failed_oclcs = get_failed_oclcs()
    all_input_files = get_input_files()
    oclcs = set()
    logging.info("Getting OCLC numbers from input files.")
    dirs = get_file_location_dict()
    for input_file in all_input_files:
        input_file_location = os.path.join(dirs['input'], input_file)
        try:
            oclc_location = validator_config.config[input_file]['oclc']
        except KeyError:
            continue
        if input_file.endswith('.mrk'):
            oclc_location = left_pad_field_number(oclc_location)
            read_marc_data(oclcs, input_file_location, oclc_location)
        elif re.search(r'\.(?:txt|tsv|csv|xlsx)$', input_file):
            try:
                has_header = validator_config.config[input_file]['header']
                if has_header == '1':
                    has_header_row = True
                else:
                    has_header_row = False
            except KeyError:
                has_header_row = False
            if input_file.endswith('xlsx'):
                read_spreadsheet_data(oclcs, input_file_location, oclc_location, has_header_row)
            else:
                read_text_data(oclcs, input_file_location, oclc_location, has_header_row)
        else:
            raise Exception("Input file of unsupported type: {}".format(input_file))
    logging.info("Checking for OCLCs to download from API.")
    local_marc_db = LocalMarcDb()
    oclcs_to_do = set()
    wc_oclcs = set()
    for oclc in oclcs:
        worldcat_seen = ''
        if not oclc or not str(oclc).isdigit() or oclc in failed_oclcs:
            continue
        record = local_marc_db.get_marc_from_db(oclc, recent_only=True)
        if not record or '=LDR  ' not in record:
            oclcs_to_do.add(oclc)
        else:
            wc_oclcs.add(oclc)
    logging.info('{} WorldCat OCLCs seen in set.'.format(len(wc_oclcs)))
    logging.info('{} OCLCs to download from API.'.format(len(oclcs_to_do)))
    return oclcs_to_do
