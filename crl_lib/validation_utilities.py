"""
A set of utilities mainly to support checking and validation of bib records.

"""

import re


def check_marc_for_hc_serial(marc):
    """
    Is a MARC record for a hard copy serial?

    Requires broadly valid MARC to work.
    """

    if not check_marc_for_hc(marc):
        return False

    m = re.search(r"=LDR\s\s.......(.)", marc)
    try:
        bib_lvl = m.group(1)
    except AttributeError:
        return False
    m = re.search(r"=008\s\s.{21}(.)", marc)
    try:
        serial_type = m.group(1)
    except AttributeError:
        return False

    if not check_serial(bib_lvl, serial_type):
        return False

    return True


# ------------------------------------------------------------------------------
# Hard copy checks
# ------------------------------------------------------------------------------


def check_marc_for_hc(marc, check_form=True, pipe_ok=False):
    """
    Is this MARC hard copy? Returns True for hard copy.

    This checks by form, media type fields, and 245 $h. A failure in any one 
    means the title is considered non-hard copy.
    """
    m = re.search(r"=008\s\s.{23}(.)", marc)
    try:
        if not check_hc_form(m.group(1), pipe_ok):
            # print(f'{m.group(1)}  {pipe_ok}')
            return False
    except AttributeError:
        return False

    # RDA fields
    media_fields = re.findall(r"=33[78]\s\s..\$a([^$]+)", marc)
    for media_field in media_fields:
        if not check_for_hc_media_type(media_field):
            return False

    # title fields
    m = re.search(r"=245\s\s[^\r\n]*\$h(^[^$]+)", marc)
    try:
        if not check_for_hc_media_type(m.group(1)):
            return False
    except AttributeError:
        pass

    return True


def check_for_hc_title_h(title_h_field):
    """
    Look at the 245 $h for a non-hard copy record.

    Returns False (is not hard copy) on suspicious words, True without them or
    with no $h at all.
    """
    if title_h_field and re.search("(?:elec|micro|mf)", title_h_field, flags=re.I):
        return False
    return True


def check_for_hc_carrier_type(carrier_type):
    """
    Is the given carrier type compatible with a hard copy record?
    """
    if not carrier_type:
        return True
    bad_carrier_types = ["compu", "micro", "mikro", "online", "video"]
    for bad_carrier_type in bad_carrier_types:
        if bad_carrier_type in carrier_type.lower():
            return False
    return True


def check_for_hc_media_type(media_type):
    """
    is the given media type compatible with a hard copy record?
    """
    if not media_type:
        return True
    bad_media_types = ["compu", "online", "micro", "mikro", "audio", "video", "projected"]
    for bad_media_type in bad_media_types:
        if bad_media_type in media_type.lower():
            return False
    return True


def check_hc_form(form, pipe_ok=False):
    """
    Check if form is hard copy.
    """
    # Assume blank form must be empty pace, not a blank string like ""
    if not form:
        return False
    # "/" is a common error for "\".
    # "r" is reprint, but a common error for hard copy form
    elif form == " " or form == "\\" or form == "/" or form == "r":
        return True
    elif form == "f":
        # braille
        return True
    elif form == "|" and pipe_ok:
        return True
    return False


def check_hc(form, media_type=None, marc=None, pipe_ok=False):
    """
    Checks form, and MARC if available, for hard copy.
    """

    # empty form must be blank space, not empty str
    if not check_hc_form(form, pipe_ok):
        return False
    if media_type and not check_for_hc_media_type(media_type):
        return False
    if marc and not check_marc_for_hc(marc, pipe_ok):
        return False
    return True


# ------------------------------------------------------------------------------
# Serials checks
# ------------------------------------------------------------------------------


def check_serial(bib_lvl, serial_type=None):
    """
    Check bib level and serial type for serial.
    """
    if not bib_lvl or bib_lvl != 's':
        return False
    valid_serial_types = {'p', 'g', 'j', 'l', 's', 't'}
    if serial_type:
        if not check_for_legal_serial_types(serial_type):
            return False
        if serial_type in {'n', 'd', 'l', 'w', 'h'}:
            return False
    return True


def check_for_legal_serial_types(serial_type):
    """
    Check for a valid serial type.
    """
    legal_serial_types = {
        "#", "d", "g", "h", "j", "l", "m", "n", "p", "r", "s", "t", "w", 
        "|", "", " ", "\\"}
    if serial_type in legal_serial_types:
        return True
    return False


def check_newspaper(serial_type):
    """
    Checks if serial type is newspaper.
    """
    if serial_type is not None and serial_type.lower() == 'n':
        return True
    return False


def check_valid_serial_form(form):
    """
    Check if a serial's form is legal.
    """
    # - None of the following
    valid_forms = {"#", "a", "b", "c", "d",
                   "f", "o", "q", "r", "s", "", " ", "|", "\\"}
    if form in valid_forms:
        return True
    return False


# -----------------------------------------------------------------------


def loose_form_match(form_1, form_2):
    """
    Allows all electronic to match, and 'r' to match regular hard copy.
    """
    forms = [form_1, form_2]
    for i in range(2):
        forms[i] = forms[i].lower()
        # allow matching of all electronic -- 'o', 'q', 's'
        forms[i] = forms[i].replace("o", "s")
        forms[i] = forms[i].replace("q", "s")
        # treat all unknowns as hard copy; use blank fro hard copy
        forms[i] = forms[i].replace("#", "")
        forms[i] = forms[i].replace("|", "")
        forms[i] = forms[i].replace("\\", "")
        # assume 'r' ('regular print reproduction') is bad cataloging & not reference to photocopies, etc.
        forms[i] = forms[i].replace("r", "")
    if forms[0] == forms[1]:
        return True
    return False


# -----------------------------------------------------------------------


def check_gov_doc(g):
    """
    Check govt_pub bit for government doc.
    """
    try:
        if re.match("[acfilmosz]", g):
            return True
        else:
            return False
    except:
        return False

# ----------------------------------------------------------------------


def check_conser(authentication_code):
    """
    Check if auth_code is CONSER.
    """
    try:
        if (authentication_code.lower() == 'pcc') or (authentication_code.lower() == 'nsdp'):
            return True
        else:
            return False
    except:
        return False

# ----------------------------------------------------------------------


def check_dlc(cat_agent):
    """
    Check if cat agent is DLC.
    """
    try:
        if cat_agent.lower() == 'dlc':

            return True
        else:
            return False
    except:
        return False

# ----------------------------------------------------------------------


def find_electronic_856(marc):
    """
    Check 856 lines & look for anything that smacks of an electronic location.
    """
    try:
        m = re.findall(r"=856\s\s([^\r\n]*)", marc)
        for line in m:
            # "u" for the URL field
            m = re.search(r"\$u([^\r\n$]+)", line)
            if m is not None:
                return m.group(1)
            # URLs are commonly, if erroneously, found in subfield a; look for URL string
            m = re.search(r"(https?:[^\r\n$]+)", line)
            if m is not None:
                return m.group(1)
    except:
        return False

# ------------------------------------------------------------------------------
# Electronic records
# ------------------------------------------------------------------------------


def find_any_electronic(marc):
    """
    Look for evidence of electronic records in MARC.
    """
    oclcs = additional_form_electronic(marc)
    if oclcs:
        return oclcs
    elif find_electronic_856(marc):
        return 'unknown_number'
    else:
        return


def find_electronic_oclcs_and_notes(marc):
    """
    Look for electronic 776s lines, return OCLC (if it exists) and also include notes ($n)
    """

    m = re.findall(r"=776\s\s([^\r\n]*)", marc)
    if len(m) == 0:
        return []
    oclcs = []
    for line in m:
        note_subfields_list = re.findall(r"\$n([$]+)", line)

        notes = "; ".join(note_subfields_list)

        oclc = 'unknown_number'
        sub_w = re.search(r"\$w\(OCoLC\)(\d+)", line)
        try:
            oclc = sub_w.group(1)
        except AttributeError:
            pass
        sub_i = re.search(r"\$i([^$]+)", line)
        try:
            if (sub_i.group(1).lower() == "online") or (sub_i.group(1).lower() == "electronic"):
                oclcs.append((oclc, notes))
                continue
        except AttributeError:
            pass
        # other possibilities that seem to always indicate an electronic version
        if re.search("online version", line, flags=re.IGNORECASE):
            oclcs.append((oclc, notes))
            continue
        elif re.search("Electronic (?:reproduction|resource|version)", line, flags=re.IGNORECASE):
            oclcs.append((oclc, notes))
            continue
        # any "online" or "electronic" in parens seems to indicate an electronic version
        elif re.search(r"\([^)]*(?:online|electronic)[^)]*\)", line, flags=re.IGNORECASE):
            oclcs.append((oclc, notes))
            continue
        # assume any subfield entirely taken by "online" means electronic
        elif re.search(r"\$.Online ?/$", line, flags=re.IGNORECASE):
            oclcs.append((oclc, notes))
            continue
    return oclcs


def additional_form_electronic(marc):
    """
    Look at 776 lines and try to guess if the linked item is electronic.
    If it is and has an OCLC number, return OCLC.
    Assumes valid MARC.
    """
    oclcs = {}

    m = re.findall(r"=776\s\s([^\r\n]*)", marc)

    if len(m) == 0:
        return

    for line in m:
        oclc = 'unknown_number'
        sub_w = re.search(r"\$w\(OCoLC\)(\d+)", line)
        try:
            oclc = sub_w.group(1)
        except AttributeError:
            pass
        sub_i = re.search(r"\$i([^$]+)", line)
        try:
            if (sub_i.group(1).lower() == "online") or (sub_i.group(1).lower() == "electronic"):
                oclcs[oclc] = 1
        except AttributeError:
            pass
        # other possibilities that seem to always indicate an electronic find_electronic_oclcs_and_notesversion
        if re.search("online version", line, flags=re.IGNORECASE):
            oclcs[oclc] = 1
        elif re.search("Electronic (?:reproduction|resource|version)", line, flags=re.IGNORECASE):
            oclcs[oclc] = 1
        # any "online" or "electronic" in parens seems to indicate an electronic version
        elif re.search(r"\([^)]*(?:online|electronic)[^)]*\)", line, flags=re.IGNORECASE):
            oclcs[oclc] = 1
        # assume any subfield entirely taken by "online" means electronic
        elif re.search(r"\$.Online ?/$", line, flags=re.IGNORECASE):
            oclcs[oclc] = 1

    if len(oclcs) >= 1:
        oclc_list = "; ".join(oclcs.keys())
        return oclc_list
    else:
        return

    
