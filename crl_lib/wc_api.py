"""
wc_api.py
====================================
Get records from the WorldCat Search API.

At present works with OCLC numbers, ISSNs, LCCNs, and SNs.

OCLC number searches by default first search the local database of
collected MARC records. This can be turned off with the flag skip_db=True,
or set to only use records collected within the last six months with the
flag recent_only=True.

ISSN searches can be set to search for records only at a specific institution
with the flag institution=library_symbol. By default ISSN searches are not
frbrized; this can be changed with the flag frbrize=True.

By default, the class returns MARC as a Unicode text string. It can
instead return MARCXML if the user sets the flag return_marcxml=True.

If the user has set a default API key, the class will use that. If a key
has not been set, one can be set with the flag user_name=name. The name
string should be lower case, and should be the same as a name in the
config.ini file in the user's preferences folder.

Sample usage:

    from crl_lib.wc_api import WcApi

    fetcher = WcApi()

    # single record from an OCLC
    marc_record = fetcher.fetch_marc_from_api(oclc_number)
    # single record from OCLC, skipping the local database
    marc_record = fetcher.fetch_marc_from_api(oclc_number, skip_db=True)
    # list of records from an LCCN, with a specific API key
    marc_list = fetcher.fetch_marc_from_api(lccn, user_name="nate")
    # change the default API key
    fetcher.name = "andy"
    # list of records from an ISSN, only in the CRL
    marc_list = fetcher.fetch_marc_from_api(issn, institution="crl")
    # a frbrized list of records from an ISSN
    marc_list = fetcher.fetch_marc_from_api(issn, frbrize=True)
    
"""

from pprint import pprint
import xml.etree.ElementTree as ET
import urllib3
from collections import Counter
import time
import sys
import logging

import crl_lib.crl_prefs
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

    def __init__(self, user_name=None, local_marc_db_location=None):
        self._name = user_name
        self.crl_marcxml = crl_lib.marcxml.CrlMarcXML()
        self.crl_api_keys = crl_lib.crl_prefs.CrlApiKeys(user_name)
        self._create_base_search_urls()
        self.search_type_map = {
            "oclc": "oclc",
            "issn": "in",
            "lccn": "dn",
            "sn": "sn"
        }
        self.local_marc_db = crl_lib.local_marc_db.LocalMarcDb(local_marc_db_location)
        self.http = urllib3.PoolManager()
        self.counter = Counter()

        logging.basicConfig(
            format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.WARNING)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name
        self.crl_api_keys.set_api_key_name(self._name)

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

    def _create_base_search_urls(self):
        """Basic search URLs, without API key, search term, etc."""
        self.base_search_strings = {
            "oclc": 'http://www.worldcat.org/webservices/catalog/content/{}?servicelevel=full&wskey={}',
            "institution": 'http://www.worldcat.org/webservices/catalog/search/srw?query=srw.{}%3D%22{}%22+and+srw.li+%3D+%22{}%22&servicelevel=full&frbrGrouping={}&maximumRecords=100&sortKeys=LibraryCount,,0&wskey={}',
            "other": 'http://www.worldcat.org/webservices/catalog/search/srw?query=srw.{}%3D%22{}%22&servicelevel=full&frbrGrouping={}&maximumRecords=100&sortKeys=LibraryCount,,0&wskey={}'
        }

    def _get_search_url(self, search_term, search_type, frbrize_string, institution):
        if search_type == "oclc":
            search_url = self.base_search_strings["oclc"].format(
                search_term,
                self.crl_api_keys.api_key
            )
        elif institution:
            search_url = self.base_search_strings["institution"].format(
                self.search_type_map[search_type],
                search_term,
                institution,
                frbrize_string,
                self.crl_api_keys.api_key
            )
        else:
            search_url = self.base_search_strings["other"].format(
                self.search_type_map[search_type],
                search_term,
                frbrize_string,
                self.crl_api_keys.api_key
            )
        return search_url

    def _fetch_from_api(self, search_url):
        while True:
            try:
                r = self.http.request('GET', search_url, timeout=3.0)
                if r.status == 200:
                    marcxml = r.data.decode('utf8')
                    return marcxml
                else:
                    # TODO: log r.status
                    return ''
            except urllib3.exceptions.MaxRetryError:
                # Almost definitely a network error orf some sort. Pause and see if it sorts itself out.
                self._pause_on_issue('MaxRetryError')


    def _pause_on_issue(self, issue_type):
        self.counter[issue_type] += 1
        logging.warning('WorldCat API download encountered {} issue.'.format(issue_type))
        if self.counter[issue_type] >= 5:
            # TODO: log the issue
            issue_msg = 'MARC fetch is quitting after 5th instance of issue {}'.format(issue_type)
            # in case the outer script wants to keep trying, reset the error counter.
            self.counter[issue_type] = 0
            logging.error('WorldCat API download failed due to 5 instances of {} issue.'.format(issue_type))
            raise WorldCatApiFailureError(issue_msg)
        issue_msg = 'MARC fetch is pausing 20 seconds after instance {} of issue {}.\n'.format(
            self.counter[issue_type], issue_type)
        sys.stderr.write(issue_msg)
        sys.stderr.flush()
        time.sleep(20)

    def _make_return_data(self, marcxml, search_type):
        """
        Make sure return data is a string or list, whichever is appropriate for
        the specific search. Convert None data to correct type.
        """
        if not marcxml:
            if search_type == "oclc":
                return ""
            return []
        marc = self.crl_marcxml.marcxml_to_marc(marcxml)
        if type(marc) is str:
            if search_type == "oclc":
                return marc
            return [marc]
        if search_type == "oclc":
            try:
                return marc[0]
            except IndexError:
                return ""
        return marc

    def fetch_marc_from_api(
        self, search_term, search_type="oclc", frbrize=False, institution=None,
        skip_db=False, recent_only=False, return_marcxml=False
    ):
        """The main function for getting MARC from the API."""
        if frbrize:
            frbrize_string = "on"
        else:
            frbrize_string = "off"

        if search_type == "oclc" and skip_db is False:
            marc = self.local_marc_db.get_marc_from_db(search_term, recent_only)
            if marc:
                return marc

        search_url = self._get_search_url(search_term, search_type, frbrize_string, institution)

        marcxml = self._fetch_from_api(search_url)
        if return_marcxml is True:
            return marcxml
        marc = self._make_return_data(marcxml, search_type)
        self.local_marc_db.collect_data_for_marc_db(marc)
        return marc
