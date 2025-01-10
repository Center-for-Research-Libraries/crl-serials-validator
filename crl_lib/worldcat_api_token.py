import datetime
import bookops_worldcat
import pymarc
from bookops_worldcat import WorldcatAccessToken, MetadataSession
from typing import Dict, Tuple, Union, List
import crl_lib.api_keys

JSON_HEADER = {"Accept": "application/atom+json"}
SCOPES = {
    "metadata": "WorldCatMetadataAPI",
    "search": "wcapi"
}


class WorldcatApiToken:

    def __init__(self, api: str="metadata", api_key: str = "", api_secret: str = "") -> None:
        if not api_key:
            api_key, api_secret = get_metadata_api_key()
        self.api = api
        self.api_key = api_key
        self.api_secret = api_secret
        self.token: Union[None, bookops_worldcat.authorize.WorldcatAccessToken] = None

    def get_token(self) -> None:
        self.token = WorldcatAccessToken(
            key=self.api_key, secret=self.api_secret, scopes=SCOPES[self.api]
        )

    def check_token(self) -> None:
        if not self.token:
            self.get_token()
        else:
            check_time = datetime.datetime.now(
                datetime.timezone.utc
            ) + datetime.timedelta(minutes=2)
            if check_time > self.token.token_expires_at:
                self.get_token()

    def fetch_marc_from_api(
        self, oclc_number: Union[int, str]
    ) -> Union[str, List[str]]:
        """
        Convenience function to match the name in the old Search API object
        """
        marc_record = self.get_marc_record_from_oclc(oclc_number)
        return marc_record

    def get_marcxml_from_oclc(self, oclc_number: Union[int, str]) -> str:
        self.check_token()
        with bookops_worldcat.MetadataSession(authorization=self.token) as session:
            result = session.bib_get(oclc_number)
            if result.status_code == 200:
                marcxml = result.text
                return marcxml
        return ""

    def get_marc_from_oclc(
        self, oclc_number: Union[int, str], return_mrc: bool = False
    ) -> str:
        marcxml = self.get_marc_xml_from_oclc(oclc_number)
        records = pymarc.marcxml.parse_xml_to_array(marcxml)
        for record in records:
            if return_mrc is True:
                return record
            return str(record)
        return ""

    def _add_oclcs_to_oclc_map(
        self,
        input_data: Union[str, int, list, set, tuple],
        oclc_map: Dict[str, str],
    ) -> None:
        if isinstance(input_data, (str, int)):
            self._check_oclc_and_add_to_map(input_data, oclc_map)
        elif isinstance(input_data, (list, tuple, set)):
            for oclc_number in input_data:
                self._add_oclcs_to_oclc_map(oclc_number, oclc_map)

    @staticmethod
    def _check_oclc_and_add_to_map(
        oclc_number: Union[int, str], oclc_map: Dict[str, str]
    ) -> None:
        oclc_str = str(oclc_number)
        if oclc_str and oclc_str.isdigit():
            oclc_map[oclc_str] = ""


def get_metadata_api_key() -> Tuple[str, str]:
    api_keys = crl_lib.api_keys.OclcApiKeys()
    for name in api_keys.api_keys:
        if api_keys.api_keys[name]["METADATA"]:
            api_key_tuple = (
                api_keys.api_keys[name]["KEY"],
                api_keys.api_keys[name]["SECRET"],
            )
            return api_key_tuple
    raise Exception("No API key for the Metadata API defined.")
