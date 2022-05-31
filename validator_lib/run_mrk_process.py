import os
import re
import logging
import datetime
from pprint import pprint

from crl_lib.marc_utilities import get_field_subfield, get_fields_subfields
from crl_lib.line_85x86x import Convert85x86x
from crl_lib.marc_fields import MarcFields
from crl_lib.marc_file_reader import MarcFileReader
from crl_lib.crl_utilities import clean_oclc

from validator_lib.validate_583s import Line583Validator
from validator_lib.utilities import get_first_last_year_from_regular_holdings
from validator_lib.supplements_and_indexes_functions import remove_supplements_from_holdings, remove_indexes_from_holdings
from validator_lib.validator_title_dict import get_immutable_title_dict
from validator_lib.validator_data import VALIDATOR_INPUT_FOLDER


class MrkProcessRunner:
    """
    Get and check data from an input MARC record. These can be LHRs or regular
    MARC files with holdings data included.
    """
    def __init__(self, input_file, input_fields):
        
        self.input_file = input_file
        self.input_file_location = os.path.join(
            VALIDATOR_INPUT_FOLDER, self.input_file)

        self.input_fields = input_fields

        self.line_583_validator = Line583Validator()

        self.error_log_header_list = [
            "Record #",
            "Bib id",
            "Holdings id",
            "OCLC #",
            "Line 245$a",
            "Validation error"
        ]

        self.errors_this_record = []
        self.error_log_fout = {'marc': None, '583': None}

        # needed holdings fields
        self.other_holdings_fields = []
        if self.input_fields:
            if 'holdings_1' in self.input_fields:
                self.other_holdings_fields.append(
                    self.input_fields['holdings_1'])
            if 'holdings_2' in self.input_fields:
                self.other_holdings_fields.append(
                    self.input_fields['holdings_2'])

    def open_error_log_file(self, log_type):
        error_log_file_name = '{}_{}_errors_{:%Y-%m-%d}.log'.format(
            self.input_file, log_type, datetime.datetime.now())
        error_log_file_location = os.path.join(
            os.getcwd(), 'logs', error_log_file_name)
        self.error_log_fout[log_type] = open(
            error_log_file_location, 'a', encoding='utf8')
        self.error_log_fout[log_type].write(
            '\t'.join(self.error_log_header_list) + '\n')

    def get_data_from_marc(self):
        seqnum = 0
        input_file_data = []
        mfr = MarcFileReader(self.input_file_location)
        for record in mfr:
            seqnum += 1
            if seqnum % 5000 == 0:
                logging.info('   ...reached record {} in {}'.format(
                    seqnum, self.input_file))
            record_dict = self.get_data_from_record(record, seqnum)
            if '583' in self.input_fields and self.input_fields['583']:
                record_dict['583_in_file'] = True
                self.line_583_validator.validate_583_lines_in_record(
                    record, record_dict)
                if record_dict['line_583_error']:
                    record_dict['errors'].append('line_583_error')
                    self.log_583_errors(seqnum, record_dict)
                    record_dict['line_583_error'] = True
                    record_dict['583_lines_validate'] = False
                elif '=583  ' in record:
                    record_dict['line_583_error'] = False
                    record_dict['583_lines_validate'] = True
            else:
                record_dict['583_in_file'] = False
            input_file_data.append(record_dict)
            self.log_marc_errors(seqnum, record_dict)
        line_583_validation_output = self.line_583_validator.get_output_data()
        return input_file_data, line_583_validation_output

    def get_data_from_record(self, record, seqnum):
        self.errors_this_record = []
        mf = MarcFields(record, log_warnings=True, debug_info='from {}'.format(
            self.input_file))
        record_dict = get_immutable_title_dict()

        record_dict['marc'] = record
        record_dict['bib_id'] = self.get_field_from_marc('bib_id', record)
        record_dict['field_852a'] = get_field_subfield(record, '852a')
        record_dict['field_852b'] = get_field_subfield(record, '852b')
        record_dict['filename'] = self.input_file
        record_dict['holdings_id'] = self.get_field_from_marc(
            'holdings_id', record)
        record_dict['local_issn'] = mf.issn_a
        record_dict['local_oclc'] = self.get_oclc_from_marc(mf, record)
        record_dict['local_title'] = mf.title
        record_dict['seqnum'] = seqnum

        if '=LDR  ' in record:
            record_dict['ldr'] = True
        if '=583  ' in record:
            record_dict['field_583'] = True

        self.get_holdings_from_marc(record, record_dict)

        self.check_for_bad_863(record, record_dict)

        marc_lines = record.split("\n")
        for marc_line in marc_lines:
            self.validate_line(marc_line.strip(), record_dict)
        return record_dict

    def validate_line(self, marc_line, record_dict):
        """
        Look for very basic issues in a MARC line.

        At the moment, this only looks for "dangling subfields", were a subfield
        starts with a blank space. This can indicate all sorts of issues with 
        the line (like a dollar sign that isn't meant to serve as an 
        indicator of a subfield), but could also be a simple typo.
        """
        # line_no = marc_line[1:4]
        line_list = marc_line.split('$')
        # line_list[0] should be line number & delimiters
        for i in range(1, len(line_list)):
            if not re.search(r"^\w", line_list[i]):
                msg = "Incomplete, Dangling, or Illegal Subfield: {}".format(
                    marc_line)
                self.errors_this_record.append(msg)
                record_dict['dangling_subfield'] = True

    def get_oclc_from_marc(self, mf, record):
        """
        OCLC from MARC, based on user's indication of its location.
        """
        oclc = ''
        if 'oclc' in self.input_fields and self.input_fields['oclc']:
            if self.input_fields['oclc'] == '035':
                oclc = mf.oclc_035
                if not oclc:
                    oclc = get_field_subfield(record, '035', 'a')
            else:
                oclc = get_field_subfield(record, self.input_fields['oclc'])
        oclc = clean_oclc(oclc)
        return oclc

    def get_field_from_marc(self, field, record):
        if field and field in self.input_fields and self.input_fields[field]:
            field_data = get_field_subfield(record, self.input_fields[field])
            return field_data
        return ''

    def get_holdings_from_marc(self, record, record_dict):
        regular_holdings_list = []
        holdings = []
        holdings_nonpublic_notes = []
        holdings_public_notes = []

        if '863' in self.input_fields and self.input_fields['863']:
            c = Convert85x86x(record)
            holdings.extend(c.output_strings)
            for output_string in c.output_strings:
                if 'supp' not in output_string.lower() and 'ind' not in output_string.lower():
                    regular_holdings_list.append(output_string)
            for output_tuple in c.output_strings_with_notes:
                if output_tuple.nonpublic_note:
                    holdings_nonpublic_notes.append(output_tuple.nonpublic_note)
                if output_tuple.public_note:
                    holdings_public_notes.append(output_tuple.public_note)
    
        if '866' in self.input_fields and self.input_fields['866']:
            for field in ['866', '867', '868']:
                field_holdings = get_fields_subfields(record, field, "a")
                holdings.extend(field_holdings)
                if field == '866':
                    regular_holdings_list.extend(field_holdings)
                for i in range(0, len(field_holdings)):
                    if field == '868' and 'ind' not in field_holdings[i].lower():
                        field_holdings[i] = 'Index ' + field_holdings[i]
                nonpublic_notes = re.findall(r"={}\s\s[^\n]*\$x([^$\n]+)", record)
                holdings_nonpublic_notes.extend(nonpublic_notes)
                public_notes = re.findall(r"={}\s\s[^\n]*\$z([^$\n]+)", record)
                holdings_public_notes.extend(public_notes)

        for other_holdings_field in self.other_holdings_fields:
            field_holdings = get_fields_subfields(record, other_holdings_field)
            holdings.extend(field_holdings)
            for output_string in field_holdings:
                regular_holdings, _, _ = remove_supplements_from_holdings(output_string)
                regular_holdings, _, _ = remove_indexes_from_holdings(regular_holdings)
                regular_holdings_list.append(regular_holdings)
    
        first_holdings_year, last_holdings_year = get_first_last_year_from_regular_holdings(regular_holdings_list)
        if first_holdings_year:
            record_dict['holdings_start'] = int(first_holdings_year)
            record_dict['holdings_end'] = int(last_holdings_year)
        else:
            record_dict['holdings_have_no_years'] = '1'
        record_dict['local_holdings'] = '; '.join(holdings)

    def check_for_bad_863(self, record, record_dict):
        if '863' in self.input_fields:
            c = Convert85x86x(record)
            if len(c.output_strings_with_notes) > len(c.output_strings):
                for output_tuple in c.output_strings_with_notes:
                    bad_863 = True
                    for output_string in c.output_strings:
                        if output_string == output_tuple.holdings:
                            bad_863 = False
                    if bad_863:
                        record_dict['bad_863_field'] = True
                        self.errors_this_record.append('Bad 863/864/865 line')
                        return

    def log_marc_errors(self, seqnum, record_dict):
        if self.errors_this_record:
            if not self.error_log_fout['marc']:
                self.open_error_log_file('marc')
            record_dict['marc_validation_error'] = True
            record_dict['errors'].append('marc_validation_error')

            for error_str in self.errors_this_record:
                self.write_error_to_log(seqnum, record_dict, 'marc', error_str)

    def log_583_errors(self, seqnum, record_dict):
        if record_dict['line_583_error']:
            if not self.error_log_fout['583']:
                self.open_error_log_file('583')
            for error_str in record_dict['line_583_error']:
                self.write_error_to_log(seqnum, record_dict, '583', error_str)

    def write_error_to_log(self, seqnum, record_dict, log_type, error_str):
        output_list = [
            str(seqnum),
            record_dict['bib_id'],
            record_dict['holdings_id'],
            record_dict['local_oclc'],
            record_dict['local_title'],
            error_str
        ]
        self.error_log_fout[log_type].write('\t'.join(output_list) + '\n')
