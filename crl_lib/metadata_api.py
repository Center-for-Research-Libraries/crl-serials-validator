"""
Interact with the WorldCat Metadata API.

Right now only limited endpoints are supported.

Basic usage:

    m = MetadataApi(api_key, api_secret)

    marc_record = m.get_marc_record_from_oclc(oclc_number)
    marc_xml = m.get_marcxml_from_oclc(oclc_number)
    map_of_oclcs_to_current_oclcs = m.get_correct_oclcs(oclc_number, oclc_number_3)  # for any number of OCLC numbers

"""

from requests import Request, Response, Session
import json
import typing

from crl_lib.oclc_oauth_session import OclcClientCredentialsGrant
from crl_lib.marcxml import CrlMarcXML


SCOPE = 'WorldCatMetadataAPI'

METADATA_URL_BASE = "https://worldcat.org"
URL_SEARCH_BASE = "https://americas.metadata.api.oclc.org/worldcat/search/v1"

MARCXML_HEADER = {"Accept": 'application/atom+xml;content="application/vnd.oclc.marc21+xml"'}
JSON_HEADER = {'Accept': 'application/atom+json'}


class MetadataApi(OclcClientCredentialsGrant):

    def __init__(self, api_key: str, api_secret: str) -> None:
        super().__init__(api_key, api_secret, SCOPE)
        self.marcxml_converter = CrlMarcXML()
    
    def get_marc_record_from_oclc(self, oclc_number: str) -> str:
        marcxml = self.get_marcxml_from_oclc(oclc_number)
        marc_list = self.marcxml_converter.marcxml_to_marc(marcxml)
        try:
            return marc_list[0]
        except IndexError:
            return ''

    def get_marcxml_from_oclc(self, oclc_number: str) -> str:
        self.check_for_valid_token()
        url = f"{METADATA_URL_BASE}/bib/data/{oclc_number}"
        r = self.oauth_session.get(url, headers=MARCXML_HEADER)
        return r.content

    def get_correct_oclcs(self, *oclc_numbers) -> typing.Dict[str, str]:
        oclc_map = {}
        if oclc_numbers and type(oclc_numbers[0]) is list:
            oclc_numbers = oclc_numbers[0]
        for oclc in oclc_numbers:
            if type(oclc) is int or str(oclc).isdigit():
                oclc_map[oclc] = None
        if not oclc_map:
            return oclc_map
        self.check_for_valid_token()
        url = f"{METADATA_URL_BASE}/bib/checkcontrolnumbers?oclcNumbers={','.join(str(i) for i in oclc_numbers)}"
        r = self.oauth_session.get(url, headers=JSON_HEADER)
        try:
            oclcs_dict = json.loads(r.content)
        except json.JSONDecodeError:
            return {}
        for title in oclcs_dict['entries']:
            requested_oclc = title['content']['requestedOclcNumber']
            try:
                current_oclc = title['content']['currentOclcNumber']
            except IndexError:
                current_oclc = ''
            if requested_oclc in oclc_map:
                oclc_map[requested_oclc] = current_oclc
            else:
                oclc_map[str(requested_oclc)] = current_oclc
        return oclc_map

    def read_local_bibliographic_data(
        self, 
        oclc_number: str, 
        inst_symbol: str='', 
        holding_library_code: str='', 
        inst: str='') -> None:
        pass

    def search_local_bibliographic_data(self, oclc_number: str) -> None:
        pass
