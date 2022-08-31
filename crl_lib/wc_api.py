"""
Frontend for interacting with the WorldCat Search and Metadata APIs as well as 
the local database of MARC record, mainly for the retrieval of MARC records 
given OCLC numbers.
    
"""

from pprint import pprint
import xml.etree.ElementTree as ET
import urllib3
from collections import Counter
import time
import sys
import logging

from crl_lib.api_keys import OclcApiKeys
from crl_lib.search_api import SearchApi
from crl_lib.metadata_api import MetadataApi
import crl_lib.marcxml
from crl_lib.crl_utilities import fix_issn, fix_lccn
import crl_lib.local_marc_db


TEST_OCLC_NUMBER = '84078'  # The Center for Research Libraries catalogue : monographs 


class WorldCatApiFailureError(Exception):
    """
    Default error class for any errors caught in WcApi.

    Currently this will only be a MaxRetryError issued by urllib3. This will almost always mean a network error of some
    sort.
    """
    pass


class WcApi:
    """
    Class for fetching MARC records from the WorldCat Search API.

    """

    def __init__(
        self, 
        user_name: str = '', 
        data_folder: str = '', 
        api_key: str = '', 
        api_secret: str = '', 
        default_api: str = 'any',  # 'search', 'metadata', or 'any'
        preferred_api: str = '',  # 'search', 'metadata', or 'any'
    ) -> None:

        self.default_api = default_api
        self.preferred_api = preferred_api
        self._name = user_name

        self.api_keys = OclcApiKeys(api_key_config_file_location=data_folder, name_for_key=user_name)

        self.local_marc_db = crl_lib.local_marc_db.LocalMarcDb(data_folder=data_folder)
        self.http = urllib3.PoolManager()
        self.counter = Counter()

        self.logger = logging.getLogger()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name
        self.api_keys.set_api_key_name(self._name)

    @property
    def return_marcxml(self):
        return self._return_marcxml

    @name.setter
    def return_marcxml(self, return_marcxml):
        if return_marcxml:
            self._return_marcxml = True
            self.crl_marcxml = crl_lib.marcxml.CrlMarcXML()
        else:
            self._return_marcxml = False
            self.crl_marcxml = None

    def set_api(self):
        if not self.preferred_api:
            pass
        elif self.preferred_api == 'search':
            pass
        elif self.preferred_api == 'metadata':
            pass

    def open_search_api(self):
        self.search_api = SearchApi(self.api_keys.api_key)

    def open_metadata_api(self):
        self.metadata_api = MetadataApi(self.api_keys.api_key, self.api_keys.api_key_secret)

    def test_search_api(self) -> bool:
        test_marc = self.search_api.fetch_marc_from_api(TEST_OCLC_NUMBER)
        if test_marc:
            return True
        return False

    def test_metadata_api(self):
        test_marc = self.metadata_api.get_marc_record_from_oclc(TEST_OCLC_NUMBER)
        if test_marc:
            return True
        return False

    def fetch_marc_from_api(
        self, search_term: str, search_type: str = "oclc", frbrize: bool = False, institution: str = '',
        skip_db: bool = False, recent_only: bool = False, return_marcxml: bool = False
    ) -> str:
        """The main function for getting MARC from the API."""
        pass
