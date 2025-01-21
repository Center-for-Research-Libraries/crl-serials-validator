"""
Various small utilities.
"""

import re
import datetime
import unidecode
from typing import Union, Optional


def punctuation_to_underscores(my_string: str) -> str:
    """
    Convert most punctuation and spaces to underscores, to help make bland strings.

    Args:
        my_string: The string to be converted.

    Returns:
        The converted string.
    """
    my_string = my_string.replace(".", "_")
    my_string = my_string.replace(",", "_")
    my_string = my_string.replace(":", "_")
    my_string = my_string.replace(";", "_")
    my_string = my_string.replace("/", "_")
    my_string = my_string.replace('"', "_")
    my_string = my_string.replace("…", "_")
    my_string = my_string.replace("-", "_")
    my_string = my_string.replace("[", "_")
    my_string = my_string.replace("]", "_")
    my_string = my_string.replace("(", "_")
    my_string = my_string.replace(")", "_")
    my_string = my_string.replace("'", "_")
    my_string = my_string.replace(" ", "_")
    my_string = re.sub("__+", "_", my_string)
    my_string = my_string.strip("_")
    return my_string


def make_bland_string(my_string: str) -> str:
    """
    Takes a string renders it lower case & without punctuation or unicode, and
    converts spaces to underscores.

    Args:
        my_string (str): The string to be converted.

    Returns:
        str: The converted string.
    """
    my_string = unidecode.unidecode(my_string)
    my_string = my_string.lower()
    my_string = re.sub("[^a-z0-9_ ]", "", my_string)
    my_string = re.sub(r"^[\s_]*", "", my_string)
    my_string = re.sub(r"[\s_]*$", "", my_string)
    my_string = re.sub(" +", "_", my_string)
    return my_string


def clean_oclc(oclc: Union[int, str]) -> str:
    """
    Removes junk commonly seen around OCLC numbers.

    "Junk" includes:
        - Leading/trailing spaces
        - Leading/trailing parentheses
        - "OCLC", "OCoLC", or the like (case insensitive)
        - "ocm" or "ocn" (case insensitive)
        - Leading zeroes
        - Forward slashes
        - Backslashes
        - Non-numeric characters

    Also converts int to str.

        Args:
        oclc (Union[int, str]): The string or integer to be cleaned.

    Returns:
        str: The cleaned OCLC number.
    """
    oclc = str(oclc)
    oclc = oclc.replace('"', "")
    oclc = re.sub("^ *", "", oclc)
    oclc = re.sub(r"\(?OCo?LC\)?", "", oclc, flags=re.I)
    oclc = re.sub("oc?[mn]", "", oclc, flags=re.I)
    oclc = re.sub("^0*", "", oclc)
    oclc = re.sub(r"\s", "", oclc)
    oclc = re.sub("/+$", "", oclc)
    oclc = re.sub("\\\\+$", "", oclc)
    oclc = re.sub(r"\D", "", oclc)
    return oclc


def validate_oclc(oclc: str) -> bool:
    """
    Returns True on valid-seeming OCLC number.

    Args:
        oclc (str): The string to be validated.

    Returns:
        bool: True if the OCLC number is valid, False otherwise.
    """
    if not oclc.isdigit():
        return False
    oclc_int = int(oclc)
    if oclc_int < 1 or oclc_int > 40000000000:
        return False
    return True


def validate_and_clean_oclc(oclc: str) -> str:
    """
    Combines OCLC validation and junk removal.

    Returns None on failure.

    Args:
        oclc (str): The string to be cleaned and validated.

    Returns:
        str: The cleaned and validated string, empty if the string is not a valid OCLC.
    """
    oclc = clean_oclc(oclc)
    if validate_oclc(oclc):
        return oclc
    return ""


def fix_issn(issn: str) -> str:
    """
    Cleans and formats an ISSN string to standard ISSN format (e.g., '1234-5678').
    Does *not* check the algorithmic validity of the ISSN.

    This function performs several operations to ensure that the input string is a valid ISSN:
        - Converts the input to a string if it isn't already.
        - Removes non-numeric characters and subfield notes.
        - Extracts the first sequence that resembles an ISSN if the input contains multiple ISSNs.
        - Ensures the ISSN does not exceed 8 characters, with digits in all but the last position.
        - Pads the ISSN with leading zeros if necessary to reach 8 characters.
        - Formats the ISSN with a dash between the fourth and fifth digits.

    Args:
        issn (str): The ISSN string to be cleaned and formatted.

    Returns:
        str: The cleaned and formatted ISSN string, or an empty string if the input
             is invalid or cannot be formatted to an ISSN.
    """

    if not issn:
        return ""

    # ISSNs without dash or x in last spot might appear as int
    issn = str(issn)

    if not re.search(r"\d", issn):
        return ""
    # cut out starting subfield note
    issn = re.sub("^ *[$|]?a", "", issn)
    # might be a long string, like "1234-5678 $z4324-2342". Cut out all but first ISSN
    issn = re.sub(r"^ *(\d\d\d\d-\d\d\d.).*", r"\1", issn)

    issn = issn.replace('"', "")
    issn = re.sub(r"^(\d\d\d\d-\d\d\d[\dXx]).*", "\\1", issn)
    issn = issn.replace("-", "")
    issn = re.sub(r"\s", "", issn)

    # sanity check -- too long
    if len(issn) > 8:
        return ""

    # sanity check -- non-digit in something other than last place in ISSN
    if not re.match(r"^\d+.$", issn):
        return ""

    # leading zeros sometimes stripped from ISSNs
    while len(issn) < 8:
        issn = "0" + issn

    issn = re.sub("(....)(....)", "\\1-\\2", issn)
    return issn


def check_for_valid_issn(issn: str) -> bool:
    """
    Validates an ISSN (International Standard Serial Number) by checking its check digit.

    This function performs the following steps:
        1. Attempts to format the input string as a valid ISSN.
        2. If the ISSN is valid, calculates a check digit based on the first seven digits.
        3. Compares the calculated check digit with the provided check digit (eighth character).

    The algorithm for ISSN validation involves multiplying the first digit by 8, the second by 7,
    and so on until the seventh digit, which is multiplied by 2. The sum of these products is
    taken modulo 11. If the result is 0, the check digit should be 0. Otherwise, the check
    digit is 11 minus the result, with 'X' representing a check digit of 10.

    Args:
        issn (str): The ISSN string to be validated.

    Returns:
        bool: True if the ISSN is valid, False otherwise.
    """

    issn = fix_issn(issn)
    if not issn:
        return False
    n = 8
    check_total = 0
    digit_string = issn[:4] + issn[5:8]
    for digit in digit_string:
        checking_digit = int(digit)
        add_to_check = checking_digit * n
        check_total += add_to_check
        n -= 1
    check_modulus = check_total % 11
    if check_modulus == 0 and str(issn[8]) == "0":
        return True
    check_digit = 11 - (check_modulus)
    if check_digit == 10 and issn[8].upper() == "X":
        return True
    elif str(check_digit) == str(issn[8]):
        return True
    return False


def fix_lccn(lccn: str) -> str:
    """
    Attempt to fix an LCCN (Library of Congress Control Number) string.
    LCCNs come in a variety of forms and there seems to be very little standardization.
    LCCN should be of the form:

        (optional 2 letter preface) (year) (six digit trailing number)

    Years before 2000 are two digit, after 2000 are four digit.

    Examples of proper LCCNs:
    (WorldCat APIs don't need spaces or hyphens in LCCN, so we'll discard those to expose more errors)

        78-914259
        SA 68-16155
        2007-391035

    If LCCN starts with a long string of numbers with no more than two letters,
    capture that & delete all after, to get around weird multi-LCCN strings and so forth

    This function performs the following steps:

        1. If the LCCN is empty, return an empty string.
        2. If the LCCN is not empty, attempt to extract the LCCN from the start of the string.
        3. Remove any whitespace from the LCCN.
        4. Remove any hyphens from the LCCN.
        5. Remove any parentheses and their contents from the LCCN.
        6. If the LCCN contains any letters after the main number string, remove them.
        7. If the LCCN contains a "//" and any characters after it, remove them.
        8. Rebuild the LCCN with the correct number of digits, preserving any leading alphabetical characters.

    Args:
        lccn (str): The LCCN string to be fixed.

    Returns:
        str: The fixed LCCN string.
    """

    if not lccn:
        return ""

    lccn = str(lccn)

    if m := re.search(r"^([a-z0-9]{2}\d{5}\d*)", lccn):
        lccn = m.group(1)

    lccn = re.sub(r"\s*", "", lccn)
    lccn = re.sub("-", "", lccn)

    # remove some junk that gets into LCCNs
    lccn = re.sub(r"\([^)]+\)", "", lccn)
    # any letters after main number string indicates a problem
    lccn = re.sub(r"(\d{3}\d*)[a-z].*$", "\\1", lccn)

    # something fairly common like agr07000531 //r872
    lccn = re.sub(" *//.*", "", lccn)

    # rebuild the LCCN with the correct number of digits
    # remove & save leading alphabetical characters -- when present, usually 2, but can be 1 or 3
    leading_characters = ""
    if m := re.search("^([a-z]{1,3})", lccn, flags=re.IGNORECASE):
        leading_characters = m.group(1)
        lccn = lccn.replace(leading_characters, "", 1)

    year = ""
    if m := re.search(r"^(\d\d)(\d\d)\d+", lccn):
        year = m.group(1)
        if year == "20":
            year = year + m.group(2)
        lccn = lccn.replace(year, "", 1)

    # add leading zeros to reach proper length of post-year string
    while len(lccn) < 6:
        lccn = "0" + lccn

    if year:
        new_lccn = leading_characters + year + lccn
        return new_lccn

    return ""
