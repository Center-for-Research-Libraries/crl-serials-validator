import collections


class FixedDict(collections.MutableMapping):
    """
    Immutable dict, taken from an answer here:
    https://stackoverflow.com/questions/14816341/define-a-python-dictionary-with-immutable-keys-but-mutable-values
    """
    def __init__(self, data):
        self.__data = data

    def __len__(self):
        return len(self.__data)

    def __iter__(self):
        return iter(self.__data)

    def __setitem__(self, k, v):
        if k not in self.__data:
            raise KeyError(k)
        self.__data[k] = v

    def __delitem__(self, k):
        raise NotImplementedError

    def __getitem__(self, k):
        return self.__data[k]

    def __contains__(self, k):
        return k in self.__data


def get_immutable_title_dict():

    base_title_dict = {
        '008_year_1': '',
        '008_year_2': '',
        '583_in_file': '',
        '583_lines_validate': '',
        'authentication_code': '',
        'bad_863_field': '',
        'bib_id': '',
        'bib_lvl': '',
        'bib_lvl_not_serial': '',
        'binding_words_in_holdings': '',
        'carrier_type': '',
        'cat_agent': '',
        'cat_lang': '',
        'completeness_words_in_holdings': '',
        'current_freq': '',
        'dangling_subfield': '',
        'dewey': '',
        'disqualifying_error_category': '',
        'disqualifying_errors': [],
        'end_including_362': '',
        'end_problem': '',
        'error_category': '',
        'errors': [],
        'field_583': '',
        'field_852a': '',
        'field_852b': '',
        'filename': '',
        'form': '',
        'form_not_print': '',
        'former_freq': '',
        'govt_pub': '',
        'has_disqualifying_error': '',
        'holdings_1': '',
        'holdings_2': '',
        'holdings_3': '',
        'holdings_end': '',
        'holdings_have_no_years': '',
        'holdings_id': '',
        'holdings_id_repeated': '',
        'holdings_id_unique': '',
        'holdings_in_wc_range': '',
        'holdings_missing': '',
        'holdings_out_of_issn_db_date_range': '',
        'holdings_out_of_range': '',
        'holdings_start': '',
        'ignored_error_category': '',
        'ignored_errors': [],
        'institution': '',
        'invalid_carrier_type': '',
        'invalid_local_issn': '',
        'invalid_local_issn': '',
        'invalid_media_type': '',
        'invalid_record': '',
        'issn_db_form_not_print': '',
        'issn_db_format': '',
        'issn_db_issn': '',
        'issn_db_serial_type': '',
        'issn_db_serial_type_not_periodical': '',
        'issn_db_title': '',
        'issn_db_year_1': '',
        'issn_db_year_2': '',
        'issn_l': '',
        'issn_mismatch': '',
        'lang': '',
        'lc_class': '',
        'ldr': '',
        'line_561_3s': '',
        'line_561_5s': '',
        'line_561_as': '',
        'line_583_error': [],
        'line_583_error_details': [],
        'lines_583_data': [],
        'local_holdings': '',
        'local_issn': '',
        'local_issn_does_not_match_issn_db': '',
        'local_issn_does_not_match_wc_issn_a': '',
        'local_oclc': '',
        'local_oclc_repeated': '',
        'local_oclc_unique': '',
        'local_title': '',
        'location': '',
        'marc': '',
        'marc_validation_error': [],
        'media_type': '',
        'missing_fields': '',
        'nonprint_words_in_holdings': '',
        'nonpublic_notes': '',
        'numbering_peculiarities': '',
        'oclc_field': '',
        'oclc_mismatch': '',
        'oclc_symbol': '',
        'oclcs_019': '',
        'other_oclcs': '',
        'place': '',
        'preceding_oclcs': '',
        'public_notes': '',
        'publisher': '',
        'record_contains_852a': '',
        'record_id': '',
        'record_type': '',
        'record_type_not_language_material': '',
        'seqnum': '',
        'serial_type': '',
        'serial_type_not_periodical': '',
        'start_including_362': '',
        'start_problem': '',
        'succeeding_oclcs': '',
        'title_h': '',
        'title_in_jstor': '',
        'title_mismatch': '',
        'uniform_title': '',
        'wc_issn_a': '',
        'wc_issn_does_not_match_issn_db_issn': '',
        'wc_line_362': '',
        'wc_oclc': '',
        'wc_oclc_repeated': '',
        'wc_oclc_unique': '',
        'wc_title': '',
    }

    fixed_title_dict = FixedDict(base_title_dict.copy())
    return fixed_title_dict
