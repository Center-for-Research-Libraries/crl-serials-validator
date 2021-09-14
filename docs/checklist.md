# Glossary of Checklist Terms

***error_category***

A list of errors seen in the set, concatenated by semicolons.

***has_disqualifying_error***

If an error that the user has defined as disqualifying appears in the error list.

***seqnum***

A simple count of records in the input data.

***bib_id***

The input record's bib_id, from the field defined by the user.

***holdings_id***

The input record's holdings_id, from the field defined by the user.

***local_oclc***

The input record's OCLC number, from the field defined by the user.

***wc_oclc***

The OCLC from the WorldCat MARC 001, as returned by the WorldCat Search API using the local OCLC number.

***oclc_mismatch***

If the local and WorldCat OCLC numbers don't match. This will almost always mean that the local record is using a superseded OCLC number.

***local_oclc_repeated***

If the local OCLC number appears more than once in the input file.

***wc_oclc_repeated***

If the WorldCat OCLC number mapped from the local OCLC number is mapped from more than one local OCLC number in the input file.

***oclcs_019***

The OCLC numbers from the WorldCat MARC 019 field.

***local_issn***

The ISSN from the local input file.

***invalid_local_issn***

If the local_issn fails the algorithm for validating correctly formed ISSNs.

***wc_issn_a***

The ISSN from the WorldCat 022 $a.

***local_issn_does_not_match_wc_issn_a***

If the local_issn does not match the wc_issn_a.

***issn_l***

The linking ISSN from the WorldCat MARC 022 $l.

***local_title***

The title from the local input file.

***wc_title***

The title from the WorldCat MARC 245 field. This uses data from the $a, $b, $p, $n, and $h.

***title_mismatch***

The title in the local input file is significantly different from the title in the WorldCat MARC. As of now this uses Levenshtein Distance, and titles are considered as matched if 90% of the characters in whichever is shorter of the local and WorldCat titles matches the longer title.

***uniform_title***

The uniform title from the WorldCat MARC 130 field.

***title_h***

Anything found in a 245 $h in the WorldCat MARC.

***publisher***

The publisher found in the WorldCat MARC. The source for this will be from the 264 $b or the first 260 $b. 

***form***

The form from the WorldCat MARC 008.

***bib_lvl***

The bib_lvl from the WorldCat MARC LDR.

***serial_type***

The serial_type from the WorldCat MARC 008.

***carrier_type***

The carrier type from any 338 in the WorldCat MARC.

***media_type***

The media type from any 338 in the WorldCat MARC.

***place***

The MARC country code from the WorldCat MARC 008.

***lang***

The MARC language code from the WorldCat MARC 008.

***govt_pub***

Any code found in the govt_pub field in the WorldCat MARC 008.

***authentication_code***

The authentication code from the WorldCat MARC 042 field.

***cat_agent***

The cataloging agency from the WorldCat MARC 040 $a.

***cat_lang***

The cataloging language from the WorldCat MARC 040 $b.

***lc_class***

The leading letters from any LC call number found in the WorldCat 050. 

***dewey***

Any Dewey number found in the WorldCat MARC 082.

***008_year_1***

The date_1 field from the WorldCat MARC 008.

***008_year_2***

The date_2 field from the WorldCat MARC 008.

***start_including_362***

A starting year for the title based on the WorldCat MARC, using the date_1 from the 008 and any starting date found in the 362.

***end_including_362***

An ending year for the title based on the WorldCat MARC, using the date_2 from the 008 and any ending date found in the 362.

***holdings_start***

The first year found in the holdings in the local input file.

***holdings_end***

The last year found in the holdings in the local input file.

***start_problem***

If the holdings_start comes before the start_including_362.

***end_problem***

If the holdings_end comes after the end_including_362.

***holdings_out_of_range***

If either start_problem or end_problem is true.

***local_holdings***

The holdings from the user-defined field(s) in the local input file.

***nonpublic_notes***

Nonpublic notes from the holdings in the local input file. These will generally be in the $x of a holdings field.

***public_notes***

Public notes from the holdings in the local input file. These will generally be in the $z of a holdings field.

***completeness_words_in_holdings***

A word or fragment that might indicate incomplete or partial holdings was found in the input file holdings statements. Currently the scripts search for the following: "inc", "compl", "miss", "lack", "without", "w/o", or "repr".

***binding_words_in_holdings***

A word or fragment was found in the holdings that might indicate that the holdings segment might be a binding note ("Bound with vol. 26 1988") rather than an actual holdings statement. The scripts currently search for "bound" or the fragment "bd w".

***nonprint_words_in_holdings***

A term was found in the holdings indicating that they might be audiovisual materials instead of hard copy. The scripts currently search for 'DVD' and 'CD'.

***wc_line_362***

The 362 lines from the WorldCat MARC, concatenated by semicolons.

***current_freq***

The current frequency from the WorldCat MARC 310 $a.

***former_freq***

The former frequency from the WorldCat MARC 321 $a. In cases where there is more than once former frequency, the scripts only include the most recent one.

***preceding_oclcs***

OCLC numbers found in the 780 (preceding titles) field in the WorldCat MARC.

***succeeding_oclcs***

OCLC numbers found in the 785 (succeeding titles) field in the WorldCat MARC.

***other_oclcs***

OCLC numbers found in the 7875 (other relationship) field in the WorldCat MARC.

***numbering_peculiarities***

Numbering peculiarities notes found in any 515 $a in the WorldCat MARC, concatenated by semicolons.

***issn_db_issn***

The ISSN returned from searching the ISSN database with the ISSN from the local input file.

***local_issn_mismatches_issn_db_issn***

If the ISSN from the local input file and the ISSN from the ISSN database don't match. This will include situations where the local ISSN did not produce any results from the ISSN database, as well as when the local ISSN does not match the ISSN database ISSN (because the local ISSN is an ISSN-y or ISSN-z in the ISSN database).

***wc_issn_mismatches_issn_db_issn***

If the ISSN from the WorldCat MARC and the ISSN from the ISSN database don't match. This will include situations where the WorldCat ISSN did not produce any results from the ISSN database, as well as when the local ISSN does not match the ISSN database ISSN (because the WorldCat ISSN is an ISSN-y or ISSN-z in the ISSN database).

***issn_db_title***

The title from the ISSN database MARC.

***issn_db_format***

The form from the 008 in the ISSN database MARC.

***issn_db_serial_type***

The serial type from the 008 in the ISSN database MARC.

***issn_db_year_1***

The date_1 from the 008 in the ISSN database MARC.

***issn_db_year_2***

The date_2 from the 008 in the ISSN database MARC.

***holdings_out_of_issn_db_date_range***

The first and/or last year found in the holdings falls outside of the publication range as determined from years in the ISSN database MARC 008 and 362 fields.
