import re
from crl_lib.marc_utilities import get_field_subfield, get_fields_subfields
import logging


LEGAL_583_SUBFIELDS = {
        'a', 'b', 'c', 'd', 'e', 'f', 'h', 'i', 'j', 'k', 'l', 'n', 'o', 'u', 
        'x', 'z', '2', '3', '5', '6', '8'}
UNSEARCHED_LEGAL_583_SUBFIELDS = ['b', 'e', 'k', '6', '8']


class Line583Validator:

    def __init__(self):

        header = ['filename', 'seqnum', 'holdings_id', 'field_852a', 'line_583_error', 'subfield_3', 'subfield_a',
                  'subfield_c',
                  'subfield_d', 'subfield_f', 'subfield_f_2', 'subfield_f_other', 'subfield_u', 'subfield_i',
                  'subfield_l', 'subfield_z', 'subfield_l_2', 'subfield_z_2', 'subfield_l_other', 'subfield_z_other',
                  'subfield_x', 'subfield_j', 'subfield_2', 'subfield_5', 'other_subfields', 'errors']
        self.output_lines = []
        self.output_lines.append(header)

    def get_output_data(self):
        return self.output_lines.copy()

    def validate_583_lines_in_record(self, record, record_dict):
        record_dict['lines_583_data'] = []
        if record_dict['field_852a']:
            record_dict['record_contains_852a'] = True
        else:
            record_dict['record_contains_852a'] = False
            record_dict['errors'].append('missing_field_852a')
        lines_583 = re.findall(r"(=583\s\s[^\r\n]+)", record)
        record_dict['line_583_error'] = []
        record_dict['line_583_error_details'] = []
        saw_committed_to_retain = False
        for line in lines_583:
            if 'committed to retain' in line.lower():
                saw_committed_to_retain = True
            self.validate_583_line(line, record_dict)

        if not saw_committed_to_retain:
            record_dict['line_583_error'].append('no_committed_to_retain_in_583')
            record_dict['line_583_error_details'].append('no_committed_to_retain_in_583')

        line_561_3s = get_fields_subfields(record, '561', '3')
        line_561_as = get_fields_subfields(record, '561', 'a')
        line_561_5s = get_fields_subfields(record, '561', '5')
        
        record_dict['line_561_3s'] = '|$3'.join(line_561_3s)
        record_dict['line_561_as'] = '|$a'.join(line_561_as)
        record_dict['line_561_5s'] = '|$5'.join(line_561_5s)

    def validate_583_line(self, line, record_dict):
        errors = []
        self.check_for_illegal_583_subfields(line, record_dict, errors)
        delimiter_1 = line[6]
        delimiter_2 = line[7]
        self.validate_delimiters(delimiter_1, delimiter_2, errors)

        subfield_3 = get_field_subfield(line, '583', '3')
        subfield_a = get_field_subfield(line, '583', 'a')
        subfield_c = get_field_subfield(line, '583', 'c')
        subfield_d = get_field_subfield(line, '583', 'd')
        subfields_f = get_fields_subfields(line, '583', 'f')
        subfield_u = get_field_subfield(line, '583', 'u')
        subfield_i = get_field_subfield(line, '583', 'i')
        subfields_l = get_fields_subfields(line, '583', 'l')
        subfields_z = get_fields_subfields(line, '583', 'z')
        subfields_x = get_fields_subfields(line, '583', 'x')
        subfield_j = get_field_subfield(line, '583', 'j')
        subfield_2 = get_field_subfield(line, '583', '2')
        subfield_5 = get_field_subfield(line, '583', '5')

        line_583_data = {
            'a': subfield_a,
            'c': subfield_c,
            'd': subfield_d,
            'i': subfield_i,
            'l': '; '.join(subfields_l),
            'z': '; '.join(subfields_z),
            'f': '; '.join(subfields_f),
            'j': subfield_j,
            '3': subfield_3,
            '5': subfield_5
        }
        record_dict['lines_583_data'].append(line_583_data)

        other_subfield_data = []
        for unsearched_subfield in UNSEARCHED_LEGAL_583_SUBFIELDS:
            subfields_data = get_fields_subfields(line, '583', unsearched_subfield)
            if subfields_data:
                for subfield_data in subfields_data:
                    subfield_data = '$' + subfield_data
                    other_subfield_data.append(subfield_data)

        if not subfield_c:
            errors.append('no_583_subfield_c')
            record_dict['line_583_error_details'].append('Missing $c in 583: {}'.format(line))
        if not subfields_f:
            errors.append('no_583_subfield_f')
            record_dict['line_583_error_details'].append('Missing $f in 583: {}'.format(line))

        output_row = [
            record_dict['filename'],
            record_dict['seqnum'],
            record_dict['holdings_id'],
            record_dict['field_852a'],
            '; '.join(errors),
            subfield_3,
            subfield_a,
            subfield_c,
            subfield_d,
        ]
        self.add_subfield_from_list_to_output(subfields_f, output_row)
        self.add_subfield_from_list_to_output(subfields_f, output_row)
        output_row.append('; '.join(subfields_f))
        output_row.append(subfield_u)
        output_row.append(subfield_i)
        self.add_subfield_from_list_to_output(subfields_l, output_row)
        self.add_subfield_from_list_to_output(subfields_z, output_row)
        self.add_subfield_from_list_to_output(subfields_l, output_row)
        self.add_subfield_from_list_to_output(subfields_z, output_row)
        output_row.append('; '.join(subfields_l))
        output_row.append('; '.join(subfields_z))
        output_row.append('; '.join(subfields_x))
        output_row.append(subfield_j)
        output_row.append(subfield_2)
        output_row.append(subfield_5)
        output_row.append('; '.join(other_subfield_data))
        output_row.append('; '.join(errors))

        self.output_lines.append(output_row)
        record_dict['line_583_error'].extend(errors)

    @staticmethod
    def add_subfield_from_list_to_output(subfield_list, output_row):
        try:
            subfield_data = subfield_list.pop(0)
            output_row.append(subfield_data)
        except IndexError:
            output_row.append('')

    def check_for_illegal_583_subfields(self, line, record_dict, errors):
        seen_subfields = set()
        split_line = line.split('$')
        split_line.pop(0)
        for segment in split_line:
            try:
                subfield = segment[0]
            except IndexError:
                # will most likely be something like doing dollar signs in the field
                subfield = ' '
            if subfield not in LEGAL_583_SUBFIELDS:
                subfield = subfield.strip()
                if subfield:
                    errors.append('illegal_583_subfield_{}'.format(subfield))
                    record_dict['line_583_error_details'].append('Illegal subfield ${} in 583: {}'.format(subfield, line))
                else:
                    errors.append('dangling_583_subfield')
                    record_dict['line_583_error_details'].append('Dangling subfield in 583: {}'.format(line))
            if subfield in seen_subfields and subfield in {'3', 'a', 'c'}:
                errors.append('multiple_583_subfield_{}'.format(subfield))
                record_dict['line_583_error_details'].append('Multiple subfield ${} in 583: {}'.format(subfield, line))
            seen_subfields.add(subfield)

    @staticmethod
    def validate_delimiters(delimiter_1, delimiter_2, errors):
        if delimiter_1 not in {'\\', '1', '0', ' '}:
            errors.append('invalid_583_first_delimiter')
            errors.append('Illegal first subfield in 583: {}'.format(delimiter_1))
        if delimiter_2 not in {'\\', ' '}:
            errors.append('invalid_583_second_delimiter')
            errors.append('Illegal second subfield in 583: {}'.format(delimiter_2))
