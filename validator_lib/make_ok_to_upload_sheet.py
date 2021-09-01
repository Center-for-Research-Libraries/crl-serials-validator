import re
import logging

from crl_lib.marc_utilities import get_field_subfield, get_fields_subfields


class UploadOKSheetMaker:
    def __init__(self, abbrev, program):

        self.logger = logging.getLogger('validator.UploadOKSheetMaker')

        header = ['issnprint', 'oclc_symbol', 'oclc_number', 'year_archived', 'method', 'institution_name',
                     'program', 'oclc_holdings_location_code', 'custodial_history', 'summary_holdings',
                     'detailed_holdings', 'local_catalog_id', 'holdings_record_id', 'archive_action', 'date_of_action',
                     'action_interval', 'validation_level', 'validation_status', 'materials_specified',
                     'site_of_action', 'public_note', 'archiving_institution']
        self.abbrev = abbrev
        self.program = program
        self.output = [header]

    def get_output(self):
        if len(self.output) <= 1:
            return []
        return self.output

    def add_title(self, input_tuple, record):
        lines_583 = get_fields_subfields(record, '583')
        for line_583 in lines_583:
            if "committed to retain" in line_583.lower():
                break
        subfields = {}
        split_line = line_583.split('$')
        split_line.pop(0)
        for segment in split_line:
            subfield = segment[0]
            subfield_data = segment[1:]
            subfields[subfield] = subfield_data

        issnprint = input_tuple.issn
        oclc_symbol = get_field_subfield(record, '852', 'a')
        oclc_number = input_tuple.oclc
        method = self.get_subfield_data(line_583, 'i')
        institution_name = ''
        subfields_f = self.get_subfield_data(line_583, 'f')
        subfields_f_list = subfields_f.split(';')
        program = subfields_f_list[0]
        oclc_holdings_location_code = ''
        custodial_history = ''
        summary_holdings = ''
        detailed_holdings = '; '.join(input_tuple.holdings)
        local_catalog_id = input_tuple.bib_id
        holdings_record_id = input_tuple.holdings_id
        archive_action = self.get_subfield_data(line_583, 'a')
        date_of_action = self.get_subfield_data(line_583, 'c')
        year_archived = date_of_action[:4]
        action_interval = self.get_subfield_data(line_583, 'd')
        validation_level = ''
        validation_status = ''
        materials_specified = self.get_subfield_data(line_583, '3')
        site_of_action = self.get_subfield_data(line_583, 'j')
        public_note = self.get_subfield_data(line_583, 'z')
        archiving_institution = self.get_subfield_data(line_583, '5')

        output_row = [issnprint, oclc_symbol, oclc_number, year_archived, method, institution_name, program,
                      oclc_holdings_location_code, custodial_history, summary_holdings, detailed_holdings,
                      local_catalog_id, holdings_record_id, archive_action, date_of_action, action_interval,
                      validation_level, validation_status, materials_specified, site_of_action, public_note,
                      archiving_institution]
        self.output.append(output_row)

    @staticmethod
    def get_subfield_data(line_583, wanted_subfield):
        subfield_data = re.findall(r'\${}([^\r\n$]+)'.format(wanted_subfield), line_583)
        return '; '.join(subfield_data)
