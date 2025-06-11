import logging

from crl_lib.wc_api import WcApi
from crl_lib.marc_fields import MarcFields, WorldCatMarcFields

from validator_lib import CRL_FOLDER


WANTED_WORLDCAT_DATA_CATEGORIES = [
    'wc_oclc', 'oclcs_019', 'wc_issn_a', 'issn_l', 'wc_title', 'uniform_title', 
    'title_h', 'publisher', 'record_type', 'form', 'bib_lvl', 'serial_type', 
    'carrier_type', 'media_type', 'place', 'lang', 'govt_pub', 
    'authentication_code', 'cat_agent', 'cat_lang', 'lc_class', 'dewey', 
    '008_year_1', '008_year_2', 'start_including_362', 'end_including_362', 
    'wc_line_362', 'current_freq', 'former_freq', 'preceding_oclcs', 
    'succeeding_oclcs', 'other_oclcs', 'numbering_peculiarities'
]


class WorldCatMarcDataExtractor:
    """
    Take a WorldCat OCLC, get the MARC and get required fields from it, then 
    send the data to the local database.

    Instantiating this object runs through every OCLC number in the local 
    database, processes them, and exports the results to the local database.

    Note that there's no analysis in this object, just pure data gathering.
    """
    def __init__(self):
        logging.info('Getting WorldCat data.')
        self.wc_api = WcApi()
        self.no_worldcat_data_found = []
        self.no_oclc_in_input = 0

    def log_worldcat_data_not_found(self):
        for oclc in self.no_worldcat_data_found:
            logging.info('No WorldCat data found for OCLC {}'.format(oclc))
        if self.no_oclc_in_input > 0:
            if self.no_oclc_in_input == 1:
                title_word = 'title'
            else:
                title_word = 'titles'
            logging.info('{} {} without an OCLC number'.format(
                self.no_oclc_in_input, title_word))
        self.no_worldcat_data_found = []
        self.no_oclc_in_input = 0

    def get_marc_fields_object_from_oclc(self, oclc):
        """
        Get a WorldCatMarcFields object from an OCLC number. Returns None if no
        MARC is found.
        """
        if not oclc or str(oclc) == 'None' or str(oclc).lower() == 'null':
            self.no_oclc_in_input += 1
            return None

        marc = self.wc_api.fetch_marc_from_api(oclc, recent_only=True)

        if not marc:
            self.no_worldcat_data_found.append(oclc)
            return None

        mf = WorldCatMarcFields(
            marc, log_warnings=True, debug_info='from WorldCat')
        return mf

    @staticmethod
    def get_worldcat_data_category(mf, cat):
        """
        Get specific data from a WorldCatMarcFields object.

        Converts all data to strings, and will return a blank string if there is
        no data object included (which should mean that the title wasn't found in
        WorldCat for one reason or another.)
        """
        if cat.startswith('wc_'):
            cat = cat.replace('wc_', '')
        elif cat.startswith('008_year'):
            cat = cat.replace('008_', '')
        elif 'including_362' in cat:
            if cat == 'start_including_362':
                cat = 'combined_start_year'
            elif cat == 'end_including_362':
                cat = 'combined_end_year'

        if mf:
            cat_data = mf.get_data(cat)
            if not cat_data and str(cat_data) != '0':
                cat_data = ''
            elif isinstance(cat_data, (list, tuple)):
                cat_data = '; '.join(cat_data)
            else:
                cat_data = str(cat_data)
            if cat == 'place' or cat == 'lang':
                cat_data = cat_data.replace('\\', '')
        else:
            cat_data = ''
        return cat_data

    def get_worldcat_marc_data(self, oclc):
        """
        Get a dict of WorldCat MARC data related to a title, from an OCLC 
        number. 
        """
        mf = self.get_marc_fields_object_from_oclc(oclc)
        worldcat_data = {}
        for cat in WANTED_WORLDCAT_DATA_CATEGORIES:
            cat_data = self.get_worldcat_data_category(mf, cat)
            worldcat_data[cat] = cat_data
        return worldcat_data
