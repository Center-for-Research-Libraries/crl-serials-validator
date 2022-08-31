"""
Frontend for interacting with the WorldCat Search and Metadata APIs as well as 
the local database of MARC record, mainly for the retrieval of MARC records 
given OCLC numbers.
    
"""

from pprint import pprint
from collections import Counter
import logging

from crl_lib.crl_file_locations import CrlFileLocations
from crl_lib.api_keys import OclcApiKeys
from crl_lib.search_api import SearchApi
from crl_lib.metadata_api import MetadataApi
import crl_lib.marcxml
from crl_lib.crl_utilities import fix_issn, fix_lccn
import crl_lib.local_marc_db


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
        preferred_api: str = 'any',  # 'search', 'metadata', or 'any'
    ) -> None:

        self.wc_api = None

        self.preferred_api = preferred_api
        self._name = user_name

        self._api_key = api_key
        self._api_secret = api_secret

        self.api_keys = OclcApiKeys(api_key_config_file_location=data_folder, name_for_key=user_name)

        if not data_folder:
            data_folder = CrlFileLocations().find_data_folder()

        self.local_marc_db = crl_lib.local_marc_db.LocalMarcDb(data_folder=data_folder)
        self.counter = Counter()

        self.logger = logging.getLogger()

        self.set_api()

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
        if self.preferred_api == 'metadata':
            self.try_metadata_api()

        if not self.wc_api:
            self.wc_api = SearchApi(self.api_keys.api_key)

    def try_metadata_api(self) -> None:
        if self.api_keys.api_key and self.api_keys.api_key_secret:
            self.wc_api = MetadataApi(self.api_keys.api_key, self.api_keys.api_key_secret)
            self.wc_api.fetch_token()
            try:
                self.wc_api._token
            except AttributeError:
                self.wc_api = None

    def fetch_marc_from_api(
        self, search_term: str, search_type: str = "oclc", frbrize: bool = False, institution: str = '',
        skip_db: bool = False, recent_only: bool = False, return_marcxml: bool = False
    ) -> str:
        """The main function for getting MARC from the API."""
        if not skip_db:
            marc_record = self.local_marc_db.get_marc_from_db(search_term, recent_only)
            if marc_record:
                return marc_record

        marc_record = self.wc_api.fetch_marc_from_api(search_term)
        return marc_record
