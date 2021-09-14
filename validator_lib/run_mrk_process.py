import os
import re
import logging
from pprint import pprint

from crl_lib.marc_utilities import get_field_subfield, get_fields_subfields
from crl_lib.line_85x86x import Convert85x86x
from crl_lib.marc_fields import MarcFields
from crl_lib.marc_file_reader import MarcFileReader
from crl_lib.crl_utilities import clean_oclc
from validator_lib.validator_config import ValidatorConfig
from validator_lib.validate_583s import Line583Validator
from validator_lib.utilities import get_first_last_year_from_regular_holdings
from validator_lib.supplements_and_indexes_functions import remove_supplements_from_holdings, remove_indexes_from_holdings


class MrkProcessRunner:
    def __init__(self, input_file):
        
        self.input_file = input_file
        self.input_file_location = os.path.join(os.getcwd(), 'input', self.input_file)

        validator_config = ValidatorConfig()
        self.input_fields = validator_config.get_input_fields(self.input_file)

        self.line_583_validator = Line583Validator()

        self.errors_this_record = []

        # needed holdings fields
        self.other_holdings_fields = []
        if self.input_fields:
            if 'holdings_1' in self.input_fields:
                self.other_holdings_fields.append(self.input_fields['holdings_1'])
            if 'holdings_2' in self.input_fields:
                self.other_holdings_fields.append(self.input_fields['holdings_2'])

    def get_data_from_marc(self):
        seqnum = 0
        input_file_data = []
        mfr = MarcFileReader(self.input_file_location)
        for record in mfr:
            seqnum += 1
            if seqnum % 5000 == 0:
                logging.info('   ...reached record {} in {}'.format(seqnum, self.input_file))
            record_dict = self.get_data_from_record(record, seqnum)
            if '583' in self.input_fields and self.input_fields['583']:
                record_dict['583_in_file'] = True
                self.line_583_validator.validate_583_lines_in_record(record, record_dict)
                if record_dict['line_583_errors']:
                    record_dict['errors'].append('line_583_error')
                    record_dict['line_583_error'] = True
                    record_dict['583_lines_validate'] = False
                elif '=583  ' in record:
                    record_dict['line_583_error'] = False
                    record_dict['583_lines_validate'] = True
            else:
                record_dict['583_in_file'] = False
            input_file_data.append(record_dict)
            self.make_record_error_output(seqnum, record_dict)
        line_583_validation_output = self.line_583_validator.get_output_data()
        return input_file_data, line_583_validation_output

    def get_data_from_record(self, record, seqnum):
        self.errors_this_record = []
        mf = MarcFields(record, log_warnings=True, debug_info='from {}'.format(self.input_file))

        record_dict = {
            'bad_863_field': '',
            'bib_id': self.get_field_from_marc('bib_id', record),
            'dangling_subfield': '',
            'errors': [],
            'field_583': '',
            'field_852a': get_field_subfield(record, '852a'),
            'filename': self.input_file,
            'holdings_1': '',
            'holdings_2': '',
            'holdings_3': '',
            'holdings_end': '',
            'holdings_id': self.get_field_from_marc('holdings_id', record),
            'holdings_missing': '',
            'holdings_have_no_years': '',
            'holdings_start': '',
            'institution': '',
            'ldr': '',
            'line_583_error': '',
            'local_holdings': '',
            'local_issn': mf.issn_a,
            'local_oclc': self.get_oclc_from_marc(mf, record),
            'local_title': mf.title,
            'location': '',
            'marc_validation_error': '',
            'nonpublic_notes': '',
            'oclc_field': '',
            'public_notes': '',
            'seqnum': seqnum,
        }

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
        # line_no = marc_line[1:4]
        line_list = marc_line.split('$')
        # line_list[0] should be line number & delimiters
        for i in range(1, len(line_list)):
            if not re.search(r"^\w", line_list[i]):
                self.errors_this_record.append("Incomplete, Dangling, or Illegal Subfield: {}".format(marc_line))
                record_dict['dangling_subfield'] = True

    def get_oclc_from_marc(self, mf, record):
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

    def make_record_error_output(self, seqnum, record_dict):
        if not record_dict['line_583_error'] and not self.errors_this_record:
            record_dict['marc_validation_error'] = False
            return
        else:
            record_dict['marc_validation_error'] = True
        record_dict['errors'].append('marc_validation_error')
        record_dict['marc_validation_error'] = True
        error_output_list = [
            "Record # {}".format(seqnum),
            "Bib id:      {}".format(record_dict['bib_id']),
            "Holdings id: {}".format(record_dict['holdings_id']),
            "OCLC #:      {}".format(record_dict['local_oclc']),
            "Line 245$a:  {}".format(record_dict['local_title']),
            ''
        ]
        error_output_list.extend(self.errors_this_record)
