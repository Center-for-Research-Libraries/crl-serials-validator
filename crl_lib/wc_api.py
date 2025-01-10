from typing import Union, List
import io
import bookops_worldcat
import pymarc
from typing import Dict, Union, List

import crl_lib.api_keys
import crl_lib.worldcat_api_token
import crl_lib.local_marc_db


JSON_HEADER = {"Accept": "application/atom+json"}


class WcApi(crl_lib.worldcat_api_token.WorldcatApiToken):
    """
    Convenience class to work with old code. Works with the WorldCat Metadata API.
    """

    def __init__(self, api_key: str = "", api_secret: str = "") -> None:
        super().__init__(api_key=api_key, api_secret=api_secret)
        self.local_marc_db = crl_lib.local_marc_db.LocalMarcDb()

    def fetch_marc_from_api(
        self,
        oclc_number: Union[str, int],
        skip_db: bool = False,
        recent_only: bool = False,
    ) -> Union[str, List[str]]:
        """Alias to maintain compatibility with old code."""
        marc_record = self.get_marc_from_oclc(
            oclc_number=oclc_number, recent_only=recent_only, skip_db=skip_db
        )
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
        self,
        oclc_number: Union[int, str],
        recent_only: bool = False,
        skip_db: bool = False,
        return_pymarc: bool = False,
    ) -> Union[str, pymarc.record.Record]:
        """
        Get a MARC record. Optionally first checks the local MARC database (if it exists), then tries WorldCat Metadata API.

        Args:
            oclc_number (Union[int, str]): OCLC number as int or str.
            recent_only (bool, optional): Only return records from local database that are less than one year old. Defaults to False.
            skip_db (bool, optional): Skip local MARC database. Defaults to False.
            return_pymarc (bool, optional): Return pymarc record. Defaults to False.

        Returns:
            Union[str, pymarc.record.Record]: MARC record as string or pymarc record.
        """
        if not skip_db:
            marc_record = self.local_marc_db.get_marc_from_db(oclc_number, recent_only)
            if marc_record:
                return marc_record
        marcxml = self.get_marcxml_from_oclc(oclc_number)
        records = pymarc.marcxml.parse_xml_to_array(io.StringIO(marcxml))
        for record in records:
            if record:
                self.local_marc_db.collect_data_for_marc_db(str(record))
            if return_pymarc is True:
                return record
            return str(record)
        return ""
