"""
search_api.py
====================================
Get records from OCLC numbers from the WorldCat Search API version 1.

At present it does not work with ISSNs, LCCNs, or SNs.

By default, the class returns MARC as a Unicode text string. It can
instead return MARCXML if the user sets the flag return_marcxml=True.

Typically this class will be used from the wc_api class.

Sample usage:

    from crl_lib.search_api import SearchApi

    fetcher = SearchApi()

    # single record from an OCLC
    marc_record = fetcher.fetch_marc_from_api(oclc_number)
    # single record from OCLC, skipping the local database
    marc_record = fetcher.fetch_marc_from_api(oclc_number, skip_db=True)
    
"""

from pprint import pprint
import xml.etree.ElementTree as ET
import urllib3
from collections import Counter
import time
import sys
import logging

import crl_lib.marcxml
from crl_lib.crl_utilities import fix_issn, fix_lccn
import crl_lib.local_marc_db


class WorldCatSearchApiFailureError(Exception):
    """
    Default error class for any errors caught in WcApi.

    Currently this will only be a MaxRetryError issued by urllib3. This will almost always mean a network error of some
    sort.
    """
    pass


class SearchApi:
    """
    Class for fetching MARC records from the WorldCat Search API.

    """

    def __init__(self, api_key: str):
        self._api_key = api_key
        self.crl_marcxml = crl_lib.marcxml.CrlMarcXML()
        self.base_search_string = 'http://www.worldcat.org/webservices/catalog/content/{}?servicelevel=full&wskey={}'
        self.http = urllib3.PoolManager()
        self.counter = Counter()
        self.logger = logging.getLogger()

    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, new_api_key):
        self._api_key = new_api_key

    @property
    def return_marcxml(self):
        return self._return_marcxml

    @return_marcxml.setter
    def return_marcxml(self, return_marcxml):
        if return_marcxml:
            self._return_marcxml = True
            self.crl_marcxml = crl_lib.marcxml.CrlMarcXML()
        else:
            self._return_marcxml = False
            self.crl_marcxml = None

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
        self.logger.warning('WorldCat API download encountered {} issue.'.format(issue_type))
        if self.counter[issue_type] >= 5:
            # TODO: log the issue
            issue_msg = 'MARC fetch is quitting after 5th instance of issue {}'.format(issue_type)
            # in case the outer script wants to keep trying, reset the error counter.
            self.counter[issue_type] = 0
            self.logger.error('WorldCat API download failed due to 5 instances of {} issue.'.format(issue_type))
            raise WorldCatSearchApiFailureError(issue_msg)
        issue_msg = 'MARC fetch is pausing 20 seconds after instance {} of issue {}.\n'.format(
            self.counter[issue_type], issue_type)
        sys.stderr.write(issue_msg)
        sys.stderr.flush()
        time.sleep(20)

    def fetch_marc_from_api(self, search_term: str, return_marcxml: bool = False) -> str:
        """The main function for getting MARC from the API."""

        search_url = self.base_search_strings["oclc"].format(search_term, self.api_key)

        marcxml = self._fetch_from_api(search_url)
        
        if not marcxml:
            return ''
        
        if return_marcxml is True:
            return marcxml

        marc = self.crl_marcxml.marcxml_to_marc(marcxml)

        try:
            return marc[0]
        except IndexError:
            return ''
