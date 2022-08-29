"""
Module for extracting data from MARC records.

There are three separate classes:

    MarcFields -- a generic base class
    WorldCatMarcFields -- a class for use with WorldCat records, or any record where the OCLC number is in the 001
    CRLMarcFields -- For use with CRL records as exported by Millennium.

Input must be a text MARC record (as from a .mrk file).

Basic usage:

    mf = MarcFields(marc_record_as_text_string)
    issn = mf.issn
    main_entry = mf.main_entry
    # alternate method for getting data
    cataloging language = mf.get_data("cat_lang")

    crl_mf = CRLMarcFields(crl_marc_record_as_text_string)
    bib_no = crl_mf.bib_no
    update_date = crl_mf.bib_no

The module works by first converting the MARC record to a dict, then querying the dict. To show the entire dict:

    print(mf.marc_dict)

"""


import re
import logging
from collections import defaultdict
from pprint import pprint
import sys

from crl_lib.crl_utilities import clean_oclc, fix_lccn, fix_issn
from crl_lib.date_utilities import return_earlier_year, return_later_year
from crl_lib.year_utilities import find_years_first_last
from crl_lib.marc_codes import language_codes, country_codes, check_for_valid_lc_class
from crl_lib.marc_utilities import get_field_subfield, get_fields_subfields

# TODO:
#   ADD COVERAGE OF 006?
#   ADD COVERAGE OF 007?

#   TODO:
#   - How to handle records with more than one LC in 050? Example is CRL
#     b10098999. The rule is that multiple LCs appear in a single line, but there are many
#     examples of multiple 050 lines.


class MarcFields:
    """"
    Class for extracting data from MARC records.

    For WorldCat-type records (i.e., records with the OCLC# in the 001), use the subclass WorldCatMarcFields.
    For CRL records, use the subclass CRLMarcFields

    Basic usage:

        # instantiate the object
        mf = MarcFields(marc_record)

        # first option for retrieving data
        issn = mf.issn
        # second option for retrieving data
        issn = mf.get_data('issn')

    All interactions with the object should either be direct, by referencing the wanted variable, or through the 
    get_data function. The __getattr__ function will dynamically call relevant functions, so it will never be necessary
    to manually call "mf.get_issn()".

    Data potentially available from the MARC record:

        alternate_issns, alternate_oclcs, authentication_code, bib_lvl, bib_no, call_no, carrier_type, cat_agent, 
        cat_date, cat_lang, category_of_material, combined_end_year, combined_start_year, conference_pub, 
        corporate_name, country, country_id, created_date, current_freq, date_type, dewey, dewey_short, 
        electronic_location, encoding_level, end_year, entry_convention, field_856u, field_856z, first_author, form, 
        former_freq, former_freqs, freq_008, frequency, govt_doc, govt_pub, holdings, imprint, isbn, isbn_z, isbns, 
        issn, issn_a, issn_l, issn_m, issn_y, issn_z, lang, language, language_id, lc_class, lc_short, lccn, 
        lccns_cancelled, line_001, line_035a, line_362, literary_form, locations, main_entry, main_entry_field, 
        media_type, meeting_name, nature_of_contents, nature_of_work, numbering_peculiarities, oclc, oclc_035, 
        oclc_location, oclcs_019, original_form, original_script, other_issns, other_oclcs, place, preceding_issns, 
        preceding_oclcs, public_note, publisher, publisher_locations, publisher_names, publisher_places, raw_isbns, 
        record_type, regularity_008, repro_type, serial_type, specific_material_designation, start_year, subjects, 
        subjects_650, subjects_651, succeeding_issns, succeeding_oclcs, suppress, title, title_h, uniform_title, 
        update_date, year_1, year_2

    Note that some of these are lists and some are strings. Most default to a blank string.

    Helpful hints:
        * The script will make a best guess as to the location of the OCLC number based on the various MARC
          rules, but libraries often don't follow those rules. A common example is an "OCoLC" in an 003, that
          should indicate that the 001 is an OCLC number, but is in fact an artifact of the import process. If you
          need to find an OCLC and know that it's in the 035 it's probably better to use mf.oclc_035 instead of
          mf.oclc.

    """

    # TODO: expand this list
    non_repeatable_fields = {'LDR', '001'}
    main_entry_fields = ["100", "110", "111", "130"]

    def __init__(self, record, record_origin=None, log_warnings=False, debug_info=''):
        """
        rather than set all vars at start, we dynamically search them when called for;
        i.e., calling for 'form' causes library to process everything in the 008 line

        debug_info is a string that will be added to any logging outputs, that might be useful for identifying the 
        source of the MARC record in question, or some other piece of useful information. Something like "from local
        catalog" might be an appropriate string.
        """
        self.log_warnings = log_warnings
        if debug_info:
            debug_info = ' {}'.format(debug_info)
        self.debug_info = debug_info

        if not record:
            if self.log_warnings:
                error_message = 'No or blank record sent to MarcFields object{}'.format(self.debug_info)
                logging.error(error_message)
            raise Exception("No record sent to MarcFields object.")

        # minimally validate and clean record
        self.marc = self.check_and_clean_record(record)
        self.marc_dict = defaultdict(list)
        self.warnings_list = []
        self.convert_mrk_to_dicts()
        self.record_origin = record_origin
        self.print_warnings()

    def __getattr__(self, attr):
        """Main entry for all requests. This will be skipped if attribute already exists."""
        try:
            func_name = 'get_{}'.format(attr)
            func = getattr(self, func_name)
            func()
            return getattr(self, attr)
        except RecursionError:
            error_message = 'Call made for invalid attribute: {}'.format(attr)
            raise Exception(error_message)

    def print_warnings(self):
        if self.warnings_list and self.log_warnings is True:
            self.get_oclc()
            for warning_message in self.warnings_list:
                if self.oclc:
                    warning_message ='{}; OCLC {}'.format(warning_message, self.oclc)
                warning_message = '{}{}'.format(warning_message, self.debug_info)
            logging.warning(warning_message)

    @staticmethod
    def check_and_clean_record(record):
        """
        Check if the record exists and meets very minimal requirements for a MARC record.
        Clean it and get it ready for our processing.
        """
        if "=LDR  " not in record:
            Exception("Record without LDR sent to MarcFields object.")
        if "\n" not in record:
            return
        # regexes require "\n"
        record = re.sub(r"\r\n*", "\n", record)
        record = re.sub(r"\r", "\n", record)
        record = re.sub(r"\n\n+", "\n", record)
        # remove empty spaces after subfields
        record = re.sub(r"(\$.) +", r"\1", record)
        # common errors that can cause issues with OCLC numbers
        oclc_errors = ["a (OCoLC)", "(OCoLC)(OCoLC)", "(OCoCLC)", "(OCoCL)", "(OCoLCO"]
        for oclc_error in oclc_errors:
            record = record.replace(oclc_error, "(OCoLC)")
        return record

    def convert_mrk_to_dicts(self):
        """
        Convert the record to a dict, to extract data from. 
        """
        pymarc_dict = {'leader': '', 'fields': []}
        marc_list = self.marc.split('\n')
        for line in marc_list:
            line = line.rstrip()
            if not line:
                continue
            field = line[1:4]
            if len(field) < 3:
                self.warnings_list.append('Invalid field {} in MARC passed to MarcFields object.'.format(field))
                continue

            try:
                if field == 'LDR' or int(field) < 10:
                    field_data = line[6:]
                    self.marc_dict[field].append(field_data)                  
                    continue
            except (TypeError, ValueError):
                self.warnings_list.append('Invalid field {} in MARC passed to MarcFields object.'.format(field))
                continue

            ind1 = line[6]
            ind2 = line[7]
            self.marc_dict[field].append({'ind1': ind1, 'ind2': ind2, 'subfields': {}})
            if field == '040':
                # 040 (cataloging source) line may have double dollar signs due to OCLC codes like "CQ$."
                line = line.replace('$$', r'{dollar}$')
                # Similar issue if last OCLC code ends with a dollar sign.
                if line.endswith('$'):
                    line = line[:-1] + r'{dollar}'
            try:
                if line[8] == '$':
                    field_list = line[9:].split('$')
                else:
                    field_list = line[8:].split('$')
                    self.warnings_list.append('No subfield indicator at start of MARC line {}'.format(line))
            except IndexError:
                print(f'ERROR FIELD {field}')
                print(self.marc)
            for subfield_data in field_list:
                try:
                    subfield = subfield_data[0]
                except IndexError:
                    self.warnings_list.append(
                        'Subfield with no data in line {}, probably an extra $ or $ at end of line'.format(field))
                    continue
                subfield_content = subfield_data[1:]
                self.marc_dict[field][-1]['subfields'].setdefault(subfield, [])
                self.marc_dict[field][-1]['subfields'][subfield].append(subfield_content)
                if field == '245':
                    self.marc_dict['title_line'].append((subfield, subfield_content))                   

        # Check for illegally duplicated subfields. Right now only looking at a few minimal fields.
        for field in self.non_repeatable_fields:
            if len(self.marc_dict[field]) > 1:
                self.warnings_list.append('Illegally repeated field {} in MARC record'.format(field))

    def _get_list_from_marc_dict(self, field, subfield=None, position=None, end_position=None):
        if field not in self.marc_dict:
            return []
        data_list = []
        for field_data in self.marc_dict[field]:
            if subfield:
                if subfield in field_data['subfields']:
                    data_list.extend(field_data['subfields'][subfield])
            else:
                data_list.append(field_data)
        if position:
            position = int(position)
            if end_position:
                end_position = int(end_position)
                for i in range(0, len(data_list)):
                    try:
                        data_list[i] = data_list[i][position:end_position]
                    except IndexError:
                        pass
            else:
                for i in range(0, len(data_list)):
                    try:
                        data_list[i] = data_list[i][position]
                    except IndexError:
                        pass
        return data_list

    def _get_string_from_marc_dict(self, field, subfield=None, position=None, end_position=None):
        data_list = self._get_list_from_marc_dict(field, subfield, position, end_position)
        if not data_list:
            return ''
        data_string = '; '.join(data_list)
        return data_string

    def get_data(self, wanted):
        """
        An alternative to __getattr__. This is especially useful for getting data from a list of categories. Example:

            for cat in ['oclc_035', 'issn', 'title', 'bib_lvl', 'form']:
                cat_data = mf.get_data(cat)

        """
        if not wanted:
            return
        wanted_data = self.__getattr__(wanted)
        return wanted_data

    @staticmethod
    def deduplicate_data_list(data_list):
        """
        Deduplicate fields like the Dewey and LCCN that are sometimes repeated for no good reason.

        Use a dict rather than a set to maintain order.
        """
        if len(data_list) <= 1:
            return data_list
        dedup_dict = {}
        for item in data_list:
            dedup_dict[item] = None
        return list(dedup_dict.keys())


    @staticmethod
    def clean_field(data):
        """repair typically messy parts in field"""
        data = re.sub(r' *[,:;] *$', '', data)
        data = data.strip()
        return data

    #### OCLC number

    def get_oclc(self):
        """
        OCLC location depends on the type of record.
        Can use "WorldCat" origin to refer to any record with OCLC in 001
        Search order for non-WorldCat records:
            079 with "ocm"/"ocn" (this will override other references to OCLC in record)
            001 when "OCoLC" in 003 --> added a warning on this, because it's sometimes coded wrong
            035 with "OCoLC"
            001 with "ocm"/"ocn"
            other idiosyncratic fields that we come across
        Note that these are the official rules for placing an OCLC. Institutions might not follow them.
        If you know an OCLC is in the 035, you should probably use "mf.oclc_035" instead of "mf.oclc".
        """
        self.oclc = ''
        self.oclc_location = ''
        while True:
            if self.record_origin == 'worldcat' or self.record_origin == 'crl':
                m = re.search(r"^(?:ocm|ocn|on)? *0*(\d+)", self.line_001)
                try:
                    self.oclc = m.group(1)
                    self.oclc_location = '001'
                    break
                except AttributeError:
                    pass
            
            # generic, or non-WorldCat, non-CRL records
            if '079' in self.marc_dict:
                line_079a = self._get_string_from_marc_dict(field='079', subfield='a')
                m = re.search(r"oc[mn]0*(\d+)", line_079a)
                try:
                    self.oclc = m.group(1)
                    self.oclc_location = '079'
                    break
                except AttributeError:
                    pass
            # note in 003 can indicate an OCLC in 001
            if '=003  ocolc' in self.marc.lower():
                m = re.search(r"(?:oc[mn])?0*(\d+)", self.line_001)
                try:
                    self.oclc = m.group(1)
                    self.oclc_location = '001'
                    break
                except AttributeError:
                    pass
            """035 line -- looks for OCLC numbers"""
            if self.oclc_035:
                self.oclc = self.oclc_035
                self.oclc_location = '035'
                break
            m = re.search(r"oc[mn]0*(\d+)", self.line_001)
            try:
                self.oclc = m.group(1)
                self.oclc_location = '001'
                break
            except AttributeError:
                pass
            break

    def get_oclc_location(self):
        self.get_oclc()

    ##### LDR data -- not repeatable

    def get_record_type(self):
        """LDR position 6, as a string"""
        self.record_type = self._get_string_from_marc_dict(field='LDR', position=6)

    def get_bib_lvl(self):
        """LDR position 7, as a string"""
        self.bib_lvl = self._get_string_from_marc_dict(field='LDR', position=7)

    def get_encoding_level(self):
        """LDR position 17, as a string"""
        self.encoding_level = self._get_string_from_marc_dict(field='LDR', position=17)

    #### 001 line -- not repeatable

    def get_line_001(self):
        """Entire 001 line, as a string"""
        self.line_001 = self._get_string_from_marc_dict(field='001')

    #### 007 data -- repeatable field

    def get_category_of_material(self):
        """007 position 0, as a list"""
        self.category_of_material = self._get_list_from_marc_dict(field='007', position='0')

    def get_specific_material_designation(self):
        """007 position 1, as a list"""
        self.specific_material_designation = self._get_list_from_marc_dict(field='007', position='1')

    #### 008 data -- not repeatable

    def get_date_type(self):
        """008 position 6, string"""
        self.date_type = self._get_string_from_marc_dict(field='008', position=6)

    def get_year_1(self):
        self.year_1 = self._get_string_from_marc_dict(field='008', position=7, end_position=11)
        self.year_1 = re.sub(r"\D", "u", self.year_1)
        self.year_1 = self.year_1.replace("0000", "uuuu")
        self.year_2 = self._get_string_from_marc_dict(field='008', position=11, end_position=15)
        self.year_2 = re.sub(r"\D", "u", self.year_2)
        self.year_2 = self.year_2.replace("0000", "uuuu")
        if self.date_type == 'r':
            self.year_1 = self.year_2
            self.year_2 = 'uuuu'

    def get_year_2(self):
        self.get_year_1()

    def get_place(self):
        self.place = self._get_string_from_marc_dict(field='008', position=15, end_position=18)
        self.place = self.place.replace('\\', '')

    def get_country(self):
        self.country = country_codes(self.place)           

    def get_country_id(self):
        self.country_id = self.place

    def get_lang(self):
        self.lang = self._get_string_from_marc_dict(field='008', position=35, end_position=38)
        self.lang = self.lang.replace('\\', '')

    def get_language(self):
        self.language = language_codes(self.lang)

    def get_language_id(self):
        self.language_id = self.lang

    def get_form(self):
        # e & f are Maps; g, k, o, & r are Visual Materials
        if re.match(r"[efgkor]", self.record_type):
            self.form = self._get_string_from_marc_dict(field='008', position=29)
        elif ((self.bib_lvl == 'a') or (self.bib_lvl == 'm')) and self.record_type == 'a':
            self.form = self._get_string_from_marc_dict(field='008', position=23)
        else:
            self.form = self._get_string_from_marc_dict(field='008', position=23)

    def get_freq_008(self):
        if self.bib_lvl in {"b", "i", "s"} and (self.record_type == 'a'):
            self.freq_008 = self._get_string_from_marc_dict(field='008', position=18)
        else:
            self.freq_008 = ''

    def get_frequency(self):
        if self.bib_lvl in {"b", "i", "s"} and (self.record_type == 'a'):
            self.frequency = self._get_string_from_marc_dict(field='008', position=18)
        else:
            self.frequency = ''

    def get_regularity_008(self):
        if self.bib_lvl in {"b", "i", "s"} and (self.record_type == 'a'):
            self.regularity_008 = self._get_string_from_marc_dict(field='008', position=19)
        else:
            self.regularity_008 = ''

    def get_serial_type(self):
        if self.bib_lvl in {"b", "i", "s"} and (self.record_type == 'a'):
            self.serial_type = self._get_string_from_marc_dict(field='008', position=21)
        else:
            self.serial_type = ''

    def get_original_form(self):
        if self.bib_lvl in {"b", "i", "s"} and (self.record_type == 'a'):
            self.original_form = self._get_string_from_marc_dict(field='008', position=22)
        else:
            self.original_form = ''

    def get_nature_of_work(self):
        if self.bib_lvl in {"b", "i", "s"} and (self.record_type == 'a'):
            self.nature_of_work = self._get_string_from_marc_dict(field='008', position=24)
        else:
            self.nature_of_work = ''

    def get_nature_of_contents(self):
        if self.bib_lvl in {"b", "i", "s"} and (self.record_type == 'a'):
            self.nature_of_contents = self._get_string_from_marc_dict(field='008', position=25, end_position=28)
        elif ((self.bib_lvl == 'a') or (self.bib_lvl == 'm')) and self.record_type == 'a':
            self.nature_of_contents = self._get_string_from_marc_dict(field='008', position=24, end_position=28)
        else:
            self.nature_of_contents = ''

    def get_govt_pub(self):
        self.govt_pub = self._get_string_from_marc_dict(field='008', position=28)

    def get_govt_doc(self):
        self.govt_doc = self.govt_pub

    def get_conference_pub(self):
        if self.bib_lvl in {"b", "i", "s"} and (self.record_type == 'a'):
            self.conference_pub = self._get_string_from_marc_dict(field='008', position=29)
        elif ((self.bib_lvl == 'a') or (self.bib_lvl == 'm')) and self.record_type == 'a':
            self.conference_pub = self._get_string_from_marc_dict(field='008', position=29)
        else:
            self.conference_pub = ''

    def get_original_script(self):
        if self.bib_lvl in {"b", "i", "s"} and (self.record_type == 'a'):
            self.original_script = self._get_string_from_marc_dict(field='008', position=33)
        else:
            self.original_script = ''

    def get_entry_convention(self):
        if self.bib_lvl in {"b", "i", "s"} and (self.record_type == 'a'):
            self.entry_convention = self._get_string_from_marc_dict(field='008', position=34)
        else:
            self.entry_convention = ''

    def get_literary_form(self):
        if ((self.bib_lvl == 'a') or (self.bib_lvl == 'm')) and self.record_type == 'a':
            self.literary_form = self._get_string_from_marc_dict(field='008', position=33)
        else:
            self.literary_form = ''

    #### 010 data -- not repeatable

    def get_lccn(self):
        lccn_list = self._get_list_from_marc_dict(field='010', subfield='a')
        new_lccn_list = []
        for lccn in lccn_list:
            lccn = fix_lccn(lccn)
            if lccn:
                new_lccn_list.append(lccn)
        self.lccn = '; '.join(self.deduplicate_data_list(lccn_list))

    def get_lccns_cancelled(self):
        self.lccns_cancelled = []
        lccns_cancelled = self._get_list_from_marc_dict(field='010', subfield='z')
        for lccn in lccns_cancelled:
            lccn = fix_lccn(lccn)
            if lccn:
                self.lccns_cancelled.append(lccn)

    #### 019 data -- not repeatable

    def get_oclcs_019(self):
        self.oclcs_019 = []
        raw_oclcs = self._get_list_from_marc_dict(field='019', subfield='a')
        for oclc in raw_oclcs:
            oclc = clean_oclc(oclc)
            if oclc:
                self.oclcs_019.append(oclc)

    #### 020 data

    def get_raw_isbns(self):
        self.raw_isbns = self._get_list_from_marc_dict(field='020', subfield='a')

    def get_isbns(self):
        self.isbns = []
        for isbn in self.raw_isbns:
            isbn = re.sub(r'^ *(\d+[Xx]?).*', r'\1', isbn)
            if isbn:
                self.isbns.append(isbn)

    def get_isbn(self):
        self.isbn = '; '.join(self.isbns)

    def get_isbn_z(self):
        self.isbn_z = self._get_list_from_marc_dict(field='020', subfield='z')

    #### 022 line data

    def _get_issn_variant_list(self, issn_subfield):
        dict_issn_list = self._get_list_from_marc_dict(field='022', subfield=issn_subfield)
        issn_list = []
        for issn in dict_issn_list:
            issn = fix_issn(issn)
            if issn:
                issn_list.append(issn)
        return issn_list

    def get_issn_a(self):
        issn_list = self._get_issn_variant_list('a')
        self.issn_a = '; '.join(issn_list)

    def get_issn(self):
        self.issn = self.issn_a

    def get_issn_l(self):
        issn_list = self._get_issn_variant_list('l')
        self.issn_l = '; '.join(issn_list)

    def get_issn_m(self):
        self.issn_m = self._get_issn_variant_list('m')

    def get_issn_y(self):
        self.issn_y = self._get_issn_variant_list('y')

    def get_issn_z(self):
        self.issn_z = self._get_issn_variant_list('z')

    #### 035 line

    def get_oclc_035(self):
        self.oclc_035 = ''

        # need either "(OCoLC)" or "ocm"/"ocn"
        regexes_for_oclc_035 = [
            r"\(OCo?LC\) *(?:oc?[mn])? *?0*(\d+)",
            r"oc[mn] *0*(\d+)"
        ]
        for regex_for_oclc_035 in regexes_for_oclc_035:
            m = re.findall(regex_for_oclc_035, self.line_035a, flags=re.I)
            if m:
                self.oclc_035 = '; '.join(m)
                break
        if not self.oclc_035:
            # the below is illegal, but seen in some data
            line_035b = self._get_string_from_marc_dict(field='035', subfield='b')
            if re.search('^oc[lmn]', line_035b):
                m = re.search(r"0*(\d+)", self.line_035a, flags=re.I)
                try:
                    self.oclc_035 = m.group(1)
                except AttributeError:
                    pass

    def get_line_035a(self):
        self.line_035a = self._get_string_from_marc_dict(field='035', subfield='a')

    #### 040 line data

    def get_cat_agent(self):
        self.cat_agent = self._get_string_from_marc_dict(field='040', subfield='a')
        self.cat_agent = self.cat_agent.replace(r'{dollar}', '$')

    def get_cat_lang(self):
        self.cat_lang = self._get_string_from_marc_dict(field='040', subfield='b')

    #### 042 line data

    def get_authentication_code(self):
        self.authentication_code = self._get_string_from_marc_dict(field='042', subfield='a')

    #### 050/090 lines

    def get_lc_class(self):
        """
        Can be in the 050 or 090 line.
        Privilege the 090 line, then go to the 050 if that doesn't work.
        """
        self.lc_class = ''
        possible_lcs = self._get_list_from_marc_dict(field='090', subfield='a')
        possible_lcs.extend(self._get_list_from_marc_dict(field='050', subfield='a'))
        for possible_lc in possible_lcs:
            # Check for something that looks like an LC class
            if re.search(r"^[A-Z]+ [A-Z]", possible_lc, flags=re.I):
                continue
            # words like "Microfilm"
            elif re.search(r"^[A-Z]+[a-z]", possible_lc):
                continue
            else:
                m = re.search(r"^([A-Z]+)", possible_lc)
                try:
                    lc = m.group(1)
                    if check_for_valid_lc_class(lc):
                        self.lc_class = lc
                        break
                except AttributeError:
                    pass

    def get_lc_short(self):
        self.lc_short = self.lc_class[:1]

    #### 082 line data

    def get_dewey(self):
        # Dewey numbers are often repeated for some reason, so we'll only take one
        deweys = self._get_list_from_marc_dict(field='082', subfield='a')
        short_deweys = set()
        for i in range(0, len(deweys)):
        # Remove everything after the first slash in the full MARC version of the Dewey number
            dewey_short = re.sub(r"^([\d.]+).*", r"\1", deweys[i])
            if dewey_short:
                short_deweys.add(dewey_short)
            deweys[i] = deweys[i].replace("/", "")
        self.dewey = '; '.join(self.deduplicate_data_list(deweys))
        self.dewey_short = '; '.join(self.deduplicate_data_list(short_deweys))

    def get_dewey_short(self):
        self.get_dewey()

    #### 1xx lines data -- main entry

    @staticmethod
    def _clean_main_entry(main_entry):
        main_entry = re.sub(r' *[;,] *$', '', main_entry)
        main_entry = main_entry.replace(',;', ';')
        return main_entry

    def get_main_entry(self):
        self.main_entry = ''
        self.main_entry_field = ''
        if self.first_author:
            self.main_entry = self.first_author
            self.main_entry_field = '100'
        elif self.meeting_name:
            self.main_entry = self.meeting_name
            self.main_entry_field = '111'
        elif self.corporate_name:
            self.main_entry = self.corporate_name
            self.main_entry_field = '110'
        elif self.uniform_title:
            self.main_entry = self.uniform_title
            self.main_entry_field = '130'

    def get_main_entry_field(self):
        self.get_main_entry()

    def get_first_author(self):
        first_author = self._get_string_from_marc_dict(field='100', subfield='a')
        self.first_author = self._clean_main_entry(first_author)

    def get_corporate_name(self):
        if '110' in self.marc_dict:
            corporate_name = self._get_list_from_marc_dict(field='110', subfield='a')
            corporate_name.extend(self._get_list_from_marc_dict(field='110', subfield='b'))
            corporate_name = ' '.join(corporate_name)
            self.corporate_name = self._clean_main_entry(corporate_name)
        else:
            self.corporate_name = self.meeting_name

    def get_meeting_name(self):
        meeting_name = self._get_string_from_marc_dict(field='111', subfield='a')
        self.meeting_name = self._clean_main_entry(meeting_name)

    def get_uniform_title(self):
        uniform_title = self._get_string_from_marc_dict(field='130', subfield='a')
        self.uniform_title = self._clean_main_entry(uniform_title)


    #### 245 line data -- not repeatable

    def get_title(self):
        self.title = ''

        for title_tuple in self.marc_dict['title_line']:
            title_subfield, subfield_data = title_tuple
            if title_subfield == 'h':
                continue
            # preserve ellipsis, with space if it exists
            subfield_data = subfield_data.replace(" ...", " \u2026")
            subfield_data = subfield_data.replace("...", "\u2026")
            subfield_data = re.sub(r" *[/.]$", "", subfield_data)
            subfield_data = self.clean_field(subfield_data)
            if title_subfield == "a":
                self.title = subfield_data.strip()
            elif title_subfield == 'b':
                self.title = self.title + ': ' + subfield_data
            elif title_subfield == 'n':
                self.title = self.title + '. ' + subfield_data
            elif title_subfield == 'p':
                self.title = self.title + '. ' + subfield_data
        if self.title and "\u2026" in self.title:
            self.title = self.title.replace(' \u2026', ' ...')
            self.title = self.title.replace('\u2026', '...')
        self.title = self.title.replace('=.', '=')
        self.title = self.title.replace('=:', '=')

    def get_title_h(self):
        line_245h = self._get_string_from_marc_dict(field='245', subfield='h')
        title_h =  re.sub(r'\].*', ']', line_245h)
        title_h =  re.sub(r'[\[\]]', '', title_h)
        self.title_h = self.clean_field(title_h)

    #### 260 and 264 lines

    def get_publisher(self):
        """
        Most recent publisher from 264/260. 
        Should be field with 3 in first indicator. If this doesn't exist, take the first seen in 264 then 260.
        """
        publisher = ''
        first_seen_publisher = ''
        blank_publisher = False

        publisher_fields = ['264', '260']

        for publisher_field in publisher_fields:
            if publisher_field in self.marc_dict and not publisher:
                for line_dict in self.marc_dict[publisher_field]:
                    if line_dict['ind1'] == '3' and not publisher:
                        try:
                            publisher =  line_dict['subfields']['b']
                        except KeyError:
                            publisher = ''
                            blank_publisher = True
                    elif not first_seen_publisher:
                        try:
                            first_seen_publisher =  line_dict['subfields']['b']
                        except KeyError:
                            pass
        
        if not publisher and not blank_publisher:
            publisher = first_seen_publisher
        publisher_list = []
        for publisher_str in publisher:
            publisher_str = self._clean_publisher_name(publisher_str)
            if publisher_str:
                publisher_list.append(publisher_str)
        self.publisher = '; '.join(publisher_list)


    def get_publisher_names(self):
        self.publisher_names = []
        publisher_names = self._get_list_from_marc_dict(field='260', subfield='b')
        publisher_names.extend(self._get_list_from_marc_dict(field='264', subfield='b'))
        for publisher_name in publisher_names:
            publisher_name = self._clean_publisher_name(publisher_name)
            if publisher_name:
                self.publisher_names.append(publisher_name)

    def get_publisher_locations(self):
        self.publisher_locations = []
        publisher_locations = self._get_list_from_marc_dict(field='260', subfield='a')
        publisher_locations.extend(self._get_list_from_marc_dict(field='264', subfield='a'))
        for publisher_location in publisher_locations:
            publisher_location = self.clean_field(publisher_location)
            if publisher_location:
                self.publisher_locations.append(publisher_location)

    def get_publisher_places(self):
        self.publisher_places = self.publisher_locations

    def get_imprint(self):
        self.imprint = self.publisher_names

    def _clean_publisher_name(self, publisher_name):
        if not publisher_name:
            return ""
        publisher_name = re.sub(r"^([^\[]+)]", "\\1", publisher_name)
        publisher_name = re.sub(r"[\s/.:;]*$", "", publisher_name)
        publisher_name = self.clean_field(publisher_name)
        return publisher_name

    #### 310 line

    def get_current_freq(self):
        """310 line - Current Publication Frequency"""
        self.current_freq = self._get_string_from_marc_dict(field="310", subfield="a")

    #### 321 line

    def get_former_freqs(self):
        """321 line(s) - Former Publication Frequency list"""
        self.former_freqs = self._get_list_from_marc_dict(field="321", subfield="a")

    def get_former_freq(self):
        """321 line(s) - Former Publication Frequency, most recent only"""
        try:
            self.former_freq = self.former_freqs[-1]
        except IndexError:
            self.former_freq = ''

    #### 362 line

    def get_line_362(self):
        """362 line -- Dates of Publication. Return the whole thing."""
        self.line_362 = []
        working_lines_362 = self._get_list_from_marc_dict(field='362', subfield='a')
        for working_line_362 in working_lines_362:
            if "library has" not in working_line_362.lower():
                self.line_362.append(working_line_362)

    def get_combined_start_year(self):
        self._get_combined_start_end_years()

    def get_start_year(self):
        self.get_start_year = self.combined_start_year()

    def get_combined_end_year(self):
        self._get_combined_start_end_years()

    def get_end_year(self):
        self.end_year = self.combined_end_year()

    def _get_combined_start_end_years(self):
        """combine the dates in 008 and 362"""
        y1 = self.year_1.replace('u', '0')
        y2 = self.year_2.replace('u', '9')
        self.combined_start_year = y1
        self.combined_end_year = y2

        for working_line_362 in self.line_362:
            # to prevent "v. 1- fall 1970-; Ceased with: vol. 34, no. 1 (2004)." returning as 1970-current
            working_line_362 = working_line_362.replace("-;", ";")
            working_line_362 = re.sub(r"- *$", "", working_line_362)
            first_last_tuple = find_years_first_last(working_line_362)
            if first_last_tuple:
                self.combined_start_year = return_earlier_year(first_last_tuple[0], y1)
                # to prevent false open-ended publication runs, only use years that are actually in the line
                if str(first_last_tuple[1]) in working_line_362:
                    self.combined_end_year = return_later_year(first_last_tuple[1], y2)

    #### 337/338 -- RDA fields

    def get_media_type(self):
        self.media_type = self._get_string_from_marc_dict(field='337', subfield='a')

    def get_carrier_type(self):
        self.carrier_type = self._get_string_from_marc_dict(field='338', subfield='a')

    #### 515 line -- repeatable

    def get_numbering_peculiarities(self):
        self.numbering_peculiarities = self._get_string_from_marc_dict(field='515', subfield='a')

    #### TODO: 533 line -- reproduction note

    #### 650/651 lines -- repeatable

    def get_subjects_650(self):
        self.subjects_650 = self._get_list_from_marc_dict(field='650', subfield='a')

    def get_subjects_651(self):
        self.subjects_651 = self._get_list_from_marc_dict(field='651', subfield='a')

    def get_subjects(self):
        self.subjects = self.subjects_650.copy()
        self.subjects.extend(self.subjects_651)

    # 776/780/785/787 lines

    def get_alternate_oclcs(self):
        self.alternate_oclcs = self._get_related_oclcs('776')
    
    def get_alternate_issns(self):
        self.alternate_issns = self._get_related_issns('776')

    def get_preceding_oclcs(self):
        self.preceding_oclcs = self._get_related_oclcs('780')

    def get_preceding_issns(self):
        self.preceding_issns = self._get_related_issns('780')

    def get_succeeding_oclcs(self):
        self.succeeding_oclcs = self._get_related_oclcs('785')

    def get_succeeding_issns(self):
        self.succeeding_issns = self._get_related_issns('785')

    def get_other_oclcs(self):
        self.other_oclcs = self._get_related_oclcs('787')

    def get_other_issns(self):
        self.other_issns = self._get_related_issns('787')

    def _get_related_oclcs(self, field):
        oclcs = []
        seen_oclcs = set()
        oclc_lines = get_fields_subfields(self.marc, field)
        for oclc_line in oclc_lines:
            # OCLCs should be in $w, but often aren't. So we'll search via regex
            new_oclcs = re.findall('OCoLC\) *0*(\d+)', oclc_line)
            for oclc in new_oclcs:
                if oclc not in seen_oclcs:
                    seen_oclcs.add(oclc)
                    oclcs.append(oclc)
        return oclcs

    def _get_related_issns(self, field):
        issns = []
        issn_fields = self._get_list_from_marc_dict(field=field, subfield='x')
        for issn_field in issn_fields:
            m = re.search(r'(\d\d\d\d-\d\d\d[\dXx])', issn_field)
            try:
                issn = m.group(1)
                issns.append(issn)
            except AttributeError:
                pass
        return issns

    #### 856 line -- electronic location

    def get_field_856u(self):
        self.field_856u = self._get_string_from_marc_dict(field='856', subfield='u')

    def get_field_856z(self):
        self.field_856z = self._get_string_from_marc_dict(field='856', subfield='z')

    def get_electronic_location(self):
        self.electronic_location = self.field_856u

    def get_public_note(self):
        self.public_note = self.field_856z


class WorldCatMarcFields(MarcFields):
    """
    MARC records from a WorldCat-like source (i.e., that have the OCLC # in the 001)
    Basic usage:
        wc_mf = WorldCatMarcFields(marc_record)

        issn = wc_mf.get_data("issn")

    See base class for fuller notes. The only difference between this and the base class is that this class
    forces the process to take whatever is in the 001 field as the OCLC number.

    """
    def __init__(self, record, record_origin='worldcat', log_warnings=False, debug_info=''):
        super().__init__(record, record_origin=record_origin, log_warnings=log_warnings, debug_info=debug_info)
        """marc as None means record failed checks in parent class"""
        if self.marc is None:
            return


class CRLMarcFields(MarcFields):
    """
    Handle a Center for Research Libraries record, with its specific fields and data.
    """
    def __init__(self, record, record_origin="crl", log_warnings=False, debug_info=''):
        self.marc = None
        super().__init__(record, record_origin=record_origin, log_warnings=log_warnings, debug_info=debug_info)
        """marc as None means record failed checks in parent class"""
        if self.marc is None:
            return

    #### CRL 590 lines

    def get_holdings(self):
        """590 line -- holdings"""
        self.holdings = self._get_list_from_marc_dict(field='590', subfield='a')

    #### CRL 099 line

    def get_call_no(self):
        """099 line -- call number"""
        self.call_no = self._get_string_from_marc_dict(field='099', subfield='a')

    #### CRL 907 line

    def get_bib_no(self):
        self.bib_no = self._get_string_from_marc_dict(field='907', subfield='a')

    def get_update_date(self):
        self.update_date = self._get_string_from_marc_dict(field='907', subfield='b')

    def get_created_date(self):
        self.created_date = self._get_string_from_marc_dict(field='907', subfield='c')

    #### CRL 998 lines -- repeatable

    def get_cat_date(self):
        self.cat_date = self._get_string_from_marc_dict(field='998', subfield='b')

    def get_repro_type(self):
        self.repro_type = self._get_string_from_marc_dict(field='998', subfield='d')

    def get_suppress(self):
        self.suppress = self._get_string_from_marc_dict(field='998', subfield='e')

    def get_locations(self):
        self.locations = self._get_list_from_marc_dict(field='998', subfield='a')
