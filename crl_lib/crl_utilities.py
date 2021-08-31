"""
Various small utilities.
"""

import re
import datetime
import sys


def get_eol():
    """
    End of line based on current OS. This generally won't be needed.
    """
    import platform
    os = platform.system()
    if os == "Windows":
        return "\r\n"
    return "\n"


def unidecode_string(string):
    """
    unicode input string to ASCII characters (though in utf-8)
    """
    import unicodedata
    out_string = unicodedata.normalize('NFKD', string).encode('ascii', 'ignore')
    # normalize produces bytes; return as utf-8
    return out_string.decode("utf-8")


def punctuation_to_underscores(string):
    """
    Convert most punctuation and spaces to underscores, to help make bland strings.
    """
    string = string.replace('.', '_')
    string = string.replace(',', '_')
    string = string.replace(':', '_')
    string = string.replace(';', '_')
    string = string.replace('/', '_')
    string = string.replace('"', '_')
    string = string.replace('…', '_')
    string = string.replace('-', '_')
    string = string.replace('[', '_')
    string = string.replace(']', '_')
    string = string.replace('(', '_')
    string = string.replace(')', '_')
    string = string.replace("'", '_')
    string = string.replace(' ', '_')
    string = re.sub("__+", "_", string)
    string = string.strip('_')
    return string


def make_bland_string(string):
    """
    Takes a string renders it lower case & without punctuation or unicode, and
    converts spaces to underscores.
    """
    string = unidecode_string(string)
    string = string.lower()
    string = re.sub("[^a-z0-9_ ]", "", string)
    string = re.sub(r"^[\s_]*", '', string)
    string = re.sub(r"[\s_]*$", '', string)
    string = re.sub(" +", '_', string)
    return string


def clean_oclc(oclc):
    """
    Removes junk commonly seen around OCLC numbers.
    Also converts int to str.
    """
    oclc = str(oclc)
    oclc = oclc.replace('"', '')
    oclc = re.sub("^ *", "", oclc)
    oclc = re.sub(r"\(?OCo?LC\)?", "", oclc, flags=re.I)
    oclc = re.sub("oc?[mn]", "", oclc, flags=re.I)
    oclc = re.sub("^0*", "", oclc)
    oclc = re.sub(r"\s", "", oclc)
    oclc = re.sub("/+$", "", oclc)
    oclc = re.sub("\\\\+$", "", oclc)
    oclc = re.sub(r'\D', '', oclc)
    return oclc


def validate_oclc(oclc):
    """
    Returns True on valid-seeming OCLC number.
    """
    try:
        oclc = int(oclc)
    except ValueError:
        return False
    # This used to have a maximum of 400000000, but I've found 019 OCLCs that are much higher than that
    if (oclc < 0) or (oclc > 40000000000):
        return False
    return True


def validate_and_clean_oclc(oclc):
    """
    Combines OCLC validation and junk removal.
    Returns None on failure.
    """
    oclc = clean_oclc(oclc)
    if validate_oclc(oclc):
        return oclc
    return None


def fix_issn(issn):
    """
    Fix an ISSN without a dash or with leading zeros not included.
    "12345" to "0001-2345" and the like.
    """
    if not issn:
        return None

    # ISSNs without dash or x in last spot might appear as int
    issn = str(issn)

    if not re.search(r"\d", issn):
        return None
    # cut out starting subfield note
    issn = re.sub("^ *[$|]?a", "", issn)
    # might be a long string, like "1234-5678 $z4324-2342". Cut out all but first ISSN
    issn = re.sub(r"^ *(\d\d\d\d-\d\d\d.).*", r'\1', issn)

    issn = issn.replace('"', '')
    issn = re.sub(r'^(\d\d\d\d-\d\d\d[\dXx]).*', '\\1', issn)
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
        issn = '0' + issn

    issn = re.sub("(....)(....)", "\\1-\\2", issn)
    return issn


def check_for_valid_issn(issn):
    """
    The last character is a check digit. Algorithm:
        1. Multiply first digit by 8, second by 7, etc to seventh by 2. Add the sums up.
        2. Take modulus 11 of the total. If modulus is 0 then check digit should be 0.
        3. Otherwise subtract the modulus from 11. This will be check digit, with 'X' standing for 10.
    """
    issn = fix_issn(issn)
    if not issn:
        return False
    n = 8
    check_total = 0
    digit_string = issn[:4] + issn[5:8]
    for digit in digit_string:
        digit = int(digit)
        add_to_check = digit * n
        check_total += add_to_check
        n -= 1
    check_modulus = check_total % 11
    if check_modulus == 0 and str(issn[8]) == '0':
        return True
    check_digit = 11 - (check_modulus)
    if check_digit == 10 and issn[8].upper() == 'X':
        return True
    elif str(check_digit) == str(issn[8]):
        return True
    return False


def fix_lccn(lccn):
    """
    LCCNs come in a variety of forms and there seems to be very little standardization.
    LCCN should be of the form:

        (optional 2 letter preface) (year) (six digit trailing number)

    Years before 2000 are two digit, after 2000 are four digit.

    Examples of proper LCCNs:
    (API doesn't need spaces or hyphens in LCCN, so we'll discard those to expose more errors)

        78-914259
        SA 68-16155
        2007-391035

    If LCCN starts with a long string of numbers with no more than two letters,
    capture that & delete all after, to get around weird multi-LCCN strings and so forth
    """
    if not lccn:
        return

    lccn = str(lccn)

    m = re.search(r"^([a-z0-9]{2}\d{5}\d*)", lccn)
    try:
        lccn = m.group(1)
    except AttributeError:
        pass

    lccn = re.sub(r"\s*", "", lccn)
    lccn = re.sub("-", "", lccn)

    # remove some junk that gets into LCCNs
    lccn = re.sub(r"\([^)]+\)", "", lccn)
    # any letters after main number string indicates a problem
    lccn = re.sub(r"(\d{3}\d*)[a-z].*$", "\\1", lccn)

    # something fairly common like agr07000531 //r872
    lccn = re.sub(' *//.*', '', lccn)

    # rebuild the LCCN with the correct number of digits
    # remove & save leading alphabetical characters -- when present, usually 2, but can be 1 or 3
    leading_characters = ""
    m = re.search("^([a-z]{1,3})", lccn, flags=re.IGNORECASE)
    try:
        leading_characters = m.group(1)
        lccn = lccn.replace(leading_characters, "", 1)
    except AttributeError:
        pass

    m = re.search(r"^(\d\d)(\d\d)\d+", lccn)
    year = ""
    try:
        year = m.group(1)
        if year == "20":
            year = year + m.group(2)
        lccn = lccn.replace(year, "", 1)
    except AttributeError:
        pass

    # add leading zeros to reach proper length of post-year string
    while len(lccn) < 6:
        lccn = "0" + lccn

    if year:
        new_lccn = leading_characters + year + lccn
        return new_lccn


def compare_two(a, b):
    """
    Compare two inputs of any type, treating None as "" and all non-None as str.
    Useful to make 1999 (int) and "1999" (str) equal.
    True for equal, False for unequal.
    """
    if not a and not b:
        return True
    if not a or not b:
        return False
    if str(a) != str(b):
        return False
    return True


def make_timestamp():
    """
    Timestamp, of form 20170922101209
    """
    stamp = '{:%Y%m%d%H%M%S}'.format(datetime.datetime.now())
    return stamp


def make_day_timestamp():
    import time
    """Timestamp of form 20181205"""
    timestamp_tuple = time.localtime()
    timestamp = "{}{mon:02d}{day:02d}".format(
        timestamp_tuple[0], mon=timestamp_tuple[1], day=timestamp_tuple[2])
    return timestamp


def make_year_month_day_timestamp():
    """Get a timestamp in the form YYYY-MM-DD"""
    d = datetime.datetime.now()
    timestamp = d.strftime("%Y-%m-%d")
    return timestamp


def get_lowest_and_highest_years(*args):
    """Get the lowest and highest years, given a list of years (that can include slash years, like "1999/2000")"""
    # TODO: Do we throw an exception or return None when we see something like "1972/1937"?
    low_year = {"int": 9999,  "str": None}
    high_year = {"int": 0, "str": None}

    for year_str in args:
        print(year_str)
        year_list = str(year_str).split("/")
        for year in year_list:
            if int(year) < low_year["int"]:
                low_year["int"] = int(year)
                low_year["str"] = year_str
            if int(year) > high_year["int"]:
                high_year["int"] = int(year)
                high_year["str"] = year_str

    return low_year["str"], high_year["str"]


def get_lowest_year(*args):
    """Get the lowest year, given a list of years (that can include slash years, like "1999/2000")"""
    low_year, _ = get_lowest_and_highest_years(*args)
    return low_year


def get_highest_year(*args):
    """Get the highest year, given a list of years (that can include slash years, like "1999/2000")"""
    _, high_year = get_lowest_and_highest_years(*args)
    return high_year


def fuzzy_year_match(year_1, year_2):
    """
    Do two years match within a single year, also allowing matches with either year in a slash year. Though explicitly
    disallow unalike slash years matching. so "1971/1972" will match with "1972", but not with "1972/1973".

    Numbers off by up to 1 either way will match.
    """
    year_1 = str(year_1)
    year_2 = str(year_2)
    if '/' in year_1 and '/' in year_2:
        if year_1 == year_2:
            return True
        return False
    years_1 = year_1.split('/')
    years_2 = year_2.split('/')
    years_1_set = set(years_1)
    for year in years_1:
        years_1_set.add(str(int(year) + 1))
        years_1_set.add(str(int(year) - 1))
    for year in years_2:
        if year in years_1_set:
            return True
    return False


def mixed_list_to_concatenated_str(input_list, delimiter='\t'):
    """
    Take a list with various types and convert to tab separated string.
    
    None is converted to blank space, tuples and sub-lists to semicolon concatenated strings.
    Everything else is converted to a string. Note that dicts and other types will fail.
    """
    for i in range(0, len(input_list)):
        if isinstance(input_list[i], (tuple, list)):
            input_list[i] = mixed_list_to_concatenated_str(input_list[i], delimiter='; ')
        # expressly convert int to str so that 0 doesn't become a blank in the next section
        elif isinstance(input_list[i], (int, float, bool)):
            input_list[i] = str(input_list[i])
        elif not input_list[i]:
            input_list[i] = ""
        else:
            input_list[i] = str(input_list[i])
    concatenated_str = delimiter.join(input_list)
    return concatenated_str


def remove_nones_from_dict(input_dict):
    """
    None values in dict to blank str.
    """
    if type(input_dict) is not dict:
        raise Exception("Input is not dict.")
    for k in input_dict.keys():
        if input_dict[k] is None:
            input_dict[k] = ''
