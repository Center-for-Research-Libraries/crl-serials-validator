class RecordData:
    __frozen = False

    def __init__(self) -> None:

        self.year_1_008 = ""
        self.year_2_008 = ""
        self.line_583_in_file = ""
        self.lines_583_validate = ""
        self.authentication_code = ""
        self.bad_863_field = ""
        self.bib_id = ""
        self.bib_lvl = ""
        self.bib_lvl_not_serial = ""
        self.binding_words_in_holdings = ""
        self.carrier_type = ""
        self.cat_agent = ""
        self.cat_lang = ""
        self.completeness_words_in_holdings = ""
        self.current_freq = ""
        self.dangling_subfield = ""
        self.dewey = ""
        self.disqualifying_error_category = ""
        self.disqualifying_errors = []
        self.bib_id_repeated = ""
        self.holdings_id_repeated = ""
        self.local_oclc_repeated = ""
        self.wc_oclc_repeated = ""
        self.end_including_362 = ""
        self.end_problem = ""
        self.error_category = ""
        self.errors = []
        self.field_583 = ""
        self.field_852a = ""
        self.field_852b = ""
        self.filename = ""
        self.form = ""
        self.form_not_print = ""
        self.former_freq = ""
        self.govt_pub = ""
        self.has_disqualifying_error = ""
        self.holdings_1 = ""
        self.holdings_2 = ""
        self.holdings_3 = ""
        self.holdings_end = ""
        self.holdings_have_no_years = ""
        self.holdings_id = ""
        self.holdings_in_wc_range = ""
        self.holdings_missing = ""
        self.holdings_out_of_issn_db_date_range = ""
        self.holdings_out_of_range = ""
        self.holdings_start = ""
        self.institution = ""
        self.invalid_carrier_type = ""
        self.invalid_local_issn = ""
        self.invalid_wc_issn_a = ""
        self.invalid_media_type = ""
        self.invalid_record = ""
        self.issn_db_form_not_print = ""
        self.issn_db_format = ""
        self.issn_db_issn = ""
        self.issn_db_serial_type = ""
        self.issn_db_serial_type_not_periodical = ""
        self.issn_db_title = ""
        self.issn_db_year_1 = ""
        self.issn_db_year_2 = ""
        self.issn_l = ""
        self.issn_mismatch = ""
        self.lang = ""
        self.lc_class = ""
        self.ldr = ""
        self.line_561_3s = ""
        self.line_561_5s = ""
        self.line_561_as = ""
        self.line_583_error = []
        self.line_583_error_details = []
        self.lines_583_data = []
        self.local_holdings = ""
        self.local_issn = ""
        self.local_issn_does_not_match_issn_db = ""
        self.local_issn_does_not_match_wc_issn_a = ""
        self.local_oclc = ""
        self.local_title = ""
        self.location = ""
        self.marc = ""
        self.marc_validation_error = []
        self.media_type = ""
        self.missing_fields = ""
        self.nonprint_words_in_holdings = ""
        self.no_issn_matches_issn_db = ""
        self.nonpublic_notes = ""
        self.numbering_peculiarities = ""
        self.oclc_field = ""
        self.oclc_mismatch = ""
        self.oclc_symbol = ""
        self.oclcs_019 = ""
        self.other_oclcs = ""
        self.place = ""
        self.preceding_oclcs = ""
        self.public_notes = ""
        self.publisher = ""
        self.record_contains_852a = ""
        self.record_id = ""
        self.record_type = ""
        self.record_type_not_language_material = ""
        self.seqnum = ""
        self.serial_type = ""
        self.serial_type_not_periodical = ""
        self.start_including_362 = ""
        self.start_problem = ""
        self.succeeding_oclcs = ""
        self.title_h = ""
        self.title_in_jstor = ""
        self.title_mismatch = ""
        self.uniform_title = ""
        self.warning_category = ""
        self.warnings = []
        self.wc_issn_a = ""
        self.wc_issn_does_not_match_issn_db = ""
        self.wc_line_362 = ""
        self.wc_oclc = ""
        self.wc_title = ""

        self.__frozen = True

    def __setattr__(self, attr, value):
        if getattr(self, "_frozen"):
            raise AttributeError("Trying to set attribute on a frozen instance")
        return super().__setattr__(attr, value)