from crl_lib.search_api import SearchApi
from crl_lib.metadata_api import MetadataApi


TEST_OCLC_NUMBER = '84078'  # The Center for Research Libraries catalogue : monographs
TEST_PHRASE = 'center for research libraries'  # phrase that will definitely be in the MARC record


def test_search_api(api_key: str) -> bool:
    """
    Check to see if the Search API works with a particular key
    """
    search_api = SearchApi(api_key=api_key)
    test_marc = search_api.fetch_marc_from_api(TEST_OCLC_NUMBER)
    if test_marc and TEST_PHRASE in test_marc.lower():
        return True
    return False


def test_metadata_api(api_key: str, api_secret: str) -> bool:
    """
    Check to see if the Metadata API works with a particulay key & secret pair
    """
    metadata_api = MetadataApi(api_key=api_key, api_secret=api_secret)
    test_marc = metadata_api.get_marc_record_from_oclc(TEST_OCLC_NUMBER)
    if test_marc and TEST_PHRASE in test_marc.lower():
        return True
    return False
