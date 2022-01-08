import sys
import re
import os
import logging
from termcolor import cprint, colored

from crl_lib.year_utilities import find_years_first_last
from validator_lib.validator_config import ValidatorConfig
from validator_lib.bulk_validator_preferences import BulkConfig


def get_unused_filename(file_location):
    """
    Check if a filename is taken. If it is, add a number increment to the old filename until
    we find an empty file. So a duplicate of "myfile.txt" would become "myfile(1).txt", then
    "myfile(2).txt", and so on.

    Fails after 999 files, to avoid runaway processes.
    """
    if not os.path.isfile(file_location):
        return file_location

    new_file_number = 0
    path_base, full_filename = os.path.split(file_location)
    base_filename = full_filename[:full_filename.rindex('.')]
    file_extension = full_filename[full_filename.rindex('.'):]
    while True:
        new_file_number += 1
        new_filename = '{}({}){}'.format(base_filename, new_file_number, file_extension)
        new_file_location = os.path.join(path_base, new_filename)
        if not os.path.isfile(new_file_location):
            return new_file_location
        if new_file_number >= 999:
            raise Exception("At least 1000 files with the base name {}. Runaway process?".format(full_filename))


def get_abbrev_from_input_filename(input_file):
    if '_AUTOGENERATED_FILE.tsv' in input_file:
        return input_file.replace('_AUTOGENERATED_FILE.tsv', '')
    working_filename = input_file.replace('DATA.', '')
    working_filename = working_filename.replace('.', '_')
    working_filename = working_filename.replace(' ', '_')
    working_filename = working_filename.split("_")
    return working_filename[0]


def left_pad_field_number(field_number):
    """SQLite stores numbers as integers, meaning '004' will be stored as '4'. Repair these fields."""
    if not field_number:
        return ''
    field_number = str(field_number)
    if not field_number.isdigit():
        return field_number
    field_number = field_number.zfill(3)
    return field_number


def check_holdings_data_for_magic_words(holdings, holdings_nonpublic_notes, holdings_public_notes, search_type):
    search_data = {
        'completeness': ['inc', 'compl', 'miss', 'lack', 'without', 'w/o', 'repr'],
        'binding': ['bound', r'bd\.? w'],
        'nonprint': [r'd\.?v\.?d\.?', r'\bc\.?d\.?\b']
    }
    all_holdings_segments_to_check = [holdings, holdings_nonpublic_notes, holdings_public_notes]

    for holdings_segment in all_holdings_segments_to_check:
        if not holdings_segment:
            continue
        holdings_segment = str(holdings_segment)
        for search_string in search_data[search_type]:
            if re.search(search_string, holdings_segment.lower()):
                return '1'
    return ''


def get_valid_serial_types():
    return {"m", "p", "\\", " ", "-", '|'}


def get_valid_forms():
    return {"r", "\\", " ", "-"}


def double_check_slash_start_year(bib_year, bib_string, holdings_year, holdings_string):
    """
    Double check holdings starts, in an attempt to be sure that 2000/2001 isn't listed as too soon for a bib start date
    of 2001.

    Returns True on a good date.
    """
    bib_year = get_earlier_of_slash_year(bib_year, bib_string)
    holdings_year = get_later_of_slash_year(holdings_year, holdings_string)
    if int(holdings_year) >= int(bib_year):
        return True
    return False


def double_check_slash_end_year(bib_year, bib_string, holdings_year, holdings_string):
    """
    Double check holdings ends, in an attempt to be sure that 2000/2001 isn't listed as too late for a bib start date
    of 2000.

    Returns True on a good date.
    """
    holdings_year = get_earlier_of_slash_year(holdings_year, holdings_string)
    bib_year = get_later_of_slash_year(bib_year, bib_string)
    if int(holdings_year) <= int(bib_year):
        return True
    return False


def get_earlier_of_slash_year(year, data_segment):
    """For the year checks functions."""
    year_regex = r'(?:1[6789]\d\d|20[01]\d|2020)'
    short_year = str(year)[2:]
    m = re.search(r'({}) *[-/] *(?:{}|{})'.format(year_regex, year, short_year), data_segment)
    if m:
        found_year = m.group(1)
        if int(found_year) < int(year):
            year = found_year
    return year


def get_later_of_slash_year(year, data_segment):
    """For the year checks functions."""
    second_year_regex = r'(?:1[6789]\d\d|20[01]\d|2020|\d\d)'
    m = re.search(r'{} *[-/] *((?:{}))\b'.format(year, second_year_regex), data_segment)
    if m:
        found_year = m.group(1)
        if len(found_year) == 2:
            found_year = str(year)[:2] + found_year
        if int(found_year) > int(year):
            year = found_year
    return year


def get_jstor_issns(validator_data_folder):
    jstor = set()
    data_files = os.listdir(validator_data_folder)
    for data_file in data_files:
        if not data_file.lower().startswith('jstor'):
            continue
        if data_file.lower().endswith('xlsx'):
            continue
        jstor_file = os.path.join(validator_data_folder, data_file)
        try:
            with open(jstor_file, 'r', encoding='utf8') as fin:
                raw_issns = [line.rstrip() for line in fin]
        except UnicodeDecodeError:
            with open(jstor_file, 'r', encoding='ascii') as fin:
                raw_issns = [line.rstrip() for line in fin]
        for issn in raw_issns:
            if not issn or '-' not in issn:
                continue
            if 'issn' in issn.lower():
                continue
            jstor.add(issn)
    return jstor


def get_first_last_year_from_regular_holdings(regular_holdings_list):
    all_first_last = []
    for regular_holdings_str in regular_holdings_list:
        first_last_tuple = find_years_first_last(regular_holdings_str)
        if first_last_tuple[0]:
            all_first_last.extend(list(first_last_tuple))
    all_first_last.sort()
    try:
        first_year = all_first_last[0]
        last_year = all_first_last[-1]
    except IndexError:
        first_year = ""
        last_year = ""
    return first_year, last_year


def print_terminal_page_header(header_str):
    header_bar = ''.join(['~' for _ in header_str])
    header_color = 'green'
    cprint(header_bar, header_color)
    cprint(header_str, header_color)
    cprint(header_bar, header_color)
    print('')
    