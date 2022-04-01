# Glossary of Disqualifying issues

***bib_lvl_not_serial***

The bib_lvl in the WorldCat MARC LDR is not `s`.

***form_not_print***

The form in the WorldCat MARC 008 is not a blank space, a backslash, `r`, or `-`.

***record_type_not_language_material***

The record_type in the WorldCat MARC LDR is not `a`.

***serial_type_not_periodical***

The serial_type in the WorldCat MARC 008 is not a blank space, a backslash, `g`, `j`, `m`, `p`, `-`, or `|`.

***invalid_carrier_type***

The WorldCat MARC 338 contains a carriertype that is not consistent with a hard copy record.

***invalid_media_type***

The WorldCat MARC 337 contains a media type that is not consistent with a hard copy record.

***issn_db_form_not_print***

The form in the ISSN database MARC 008 is not a blank space, a backslash, `r`, or `-`.

***issn_db_serial_type_not_periodical***

The serial_type in the ISSN database MARC 008 is not a blank space, a backslash, `g`, `j`, `m`, `p`, `-`, or `|`.

***no_oclc_number***

Nothing that looks like an OCLC number was found in the original input data.

***no_worldcat_record***

No MARC record was returned from the WorldCat Search API.

***binding_words_in_holdings***

A word or fragment was found in the holdings that might indicate that the holdings segment might be a binding note ("Bound with vol. 26 1988") rather than an actual holdings statement. The scripts currently search for "bound" or the fragment "bd w".

***completeness_words_in_holdings***

A word or fragment that might indicate incomplete or partial holdings was found in the input file holdings statements. Currently the scripts search for the following: "inc", "compl", "miss", "lack", "without", "w/o", or "repr".

***nonprint_words_in_holdings***

A term was found in the holdings indicating that they might be audiovisual materials instead of hard copy. The scripts currently search for 'DVD' and 'CD'.

***duplicate_holdings_id***

The holdings_id appears more than once in the input set.

***duplicate_local_oclc***

The local OCLC number appears more than once in the input file.

***duplicate_wc_oclc***

The WorldCat OCLC number is mapped to by more than once OCLC number in the local input file.

***holdings_out_of_range***

A year was found in the holdings data outside of the publication years as determined by the 008 date_1 and date_2 and any 362 lines in the WorldCat MARC.

***holdings_out_of_issn_db_date_range***

A year was found in the holdings data outside of the publication years as determined by the 008 date_1 and date_2 and any 362 lines in the ISSN database MARC.

***invalid_local_issn***

The ISSN in the local input data fails the [algorithm for checking for valid ISSNs](https://en.wikipedia.org/wiki/International_Standard_Serial_Number#Code_format).

***issn_mismatch***

The ISSN from the local input file mismatches both the ISSN in the WorldCat MARC and the ISSN database.

***local_issn_does_not_match_wc_issn_a***

If the ISSN from the WorldCat MARC and the ISSN from the ISSN database don't match. This will include situations where the WorldCat ISSN did not produce any results from the ISSN database, as well as when the local ISSN does not match the ISSN database ISSN (because the WorldCat ISSN is an ISSN-y or ISSN-z in the ISSN database).

***local_issn_does_not_match_issn_db***

If the ISSN from the local input file and the ISSN from the ISSN database don't match. This will include situations where the local ISSN did not produce any results from the ISSN database, as well as when the local ISSN does not match the ISSN database ISSN (because the local ISSN is an ISSN-y or ISSN-z in the ISSN database).

***oclc_mismatch***

The OCLC number from the local input file does not match the OCLC number from the WorldCat MARC 001. This is almost always due to a superseded OCLC number.

***title_mismatch***

The title in the local input file is significantly different from the title in the WorldCat MARC. As of now this uses Levenshtein Distance, and titles are considered as matched if 90% of the characters in whichever is shorter of the local and WorldCat titles matches the longer title.

***line_583_error***

A 583 line in an input LHR is invalid in some way.

***marc_validation_error***

A MARC input file is invalid in some way.

***missing_field_852a***

An input LHR does not contain an 852 $a.
