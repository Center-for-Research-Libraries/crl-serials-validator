"""
year_utilities

Script for finding years in text strings, mainly holdings statements.
Right now it basically works in most cases.

A lot of work needs to be done to rationalize and organize it.
Because it's translated from Perl, it's not always so good about returning a 
consistent type (int, str, or None).

Some usages:

    list_of_years = return_all_years_in_range(string_with_years)
    # [1972, 1973, 1974, 1977, 1979, 1980]

    first_year, last_year = find_years_first_last(string_with_years)
    # 1972, 1980

    concatenated_year_string = get_concatenated_year_range(string_with_years)
    # "1972-1974, 1977, 1979-1980"

"""

import argparse
import re
import datetime
import sys
# from pprint import pprint

try:
    from crl_lib.months_finder import normalize_seasons_in_string, normalize_months_in_string
except ModuleNotFoundError:
    from months_finder import normalize_seasons_in_string, normalize_months_in_string



def return_all_years_in_range(first, last):
    my_years = []
    if check_for_valid_year(first) and check_for_valid_year(last):
        year = first
        while year <= last:
            my_years.append(year)
            year += 1
    return my_years


# ---------------------------------------------------------------------------------------------------------------------


def find_start_end_years_marc(record):
    """
    look for start and end years in a MARC record
    start with dates from 008, then look for years in 362
    """
    # 008 line -- first year, second year
    # Including a separate start/end year, that will take 362 years if different
    m = re.search(r'=008 {2}.{7}(....)(....)', record)
    try:
        start = m.group(1)
        end = m.group(2)
    except AttributeError:
        # something weird; return nothing & fail
        return

    # get rid of anomalous characters in the years, and treat them as 'unknown'
    start = re.sub(r"\D", "u", start)
    end = re.sub(r"\D", "u", end)

    # convert "unknown" into conservative dates
    start = re.sub(r"u", "9", start)
    end = re.sub(r"u", "0", end)

    start = int(start)
    end = int(end)

    # Compare dates found in the 362 to dates found in the 008.
    # Looking for dates like 1997/98, when 008 lists a 1998 start date or 1997 end date.
    # Used these to amend 'start_year''start_year' and 'end_year' hash items.
    if '=362  ' in record:
        lines_362 = re.findall(r"=362 {2}..\$.([^\n]+)", record)
        for line in lines_362:
            found_first, found_last = find_years_first_last(line)
            if found_first:
                if found_first < start:
                    start = found_first

                if found_last > end:
                    end = found_last

    return start, end


def find_years_first_last(holdings):
    """
    Send input to routine to find the whole run
    Then skim off first/last dates
    """

    years_list = find_years_all(holdings)

    if not years_list or len(years_list) == 0:
        return "", ""

    if len(years_list) == 1:
        return years_list[0], years_list[0]
    else:
        return years_list[0], years_list[-1]


def find_open_year_ranges(input_string):
    """
    look for ranges like (2004- ) and return them
    to be used in addition to something like find_years_all, which does not account for open ranges
    """
    m = re.search(r"(\d\d\d\d) ?- ?\)", input_string)
    try:
        if check_for_valid_year(m.group(1)):
            return int(m.group(1))
    except AttributeError:
        pass

    m = re.search(r"(\d\d\d\d) *\)? *- *X;$", input_string)
    try:
        if check_for_valid_year(m.group(1)):
            return int(m.group(1))
    except AttributeError:
        pass

    # slash years -- 1998/99
    m = re.match(r"(\d\d)\d\d/(\d\d) *\)? *- *\)", input_string)
    try:
        new_year = m.group(1) + m.group(2)
        if check_for_valid_year(new_year):
            return int(new_year)
    except AttributeError:
        pass

    m = re.search(r"(\d\d)\d\d/(\d\d) *\)? *- *X;$", input_string)
    try:
        new_year = m.group(1) + m.group(2)
        if check_for_valid_year(new_year):
            return int(new_year)
    except AttributeError:
        pass
    return


def find_years_all(input_string):
    """
    find every year, and return all individual years in a range like (1848-1862)
    we will assume that a slash year (1943/1944) will return both/all years in slash
    """
    if not input_string:
        return []
    input_string = str(input_string)
    # normalizing months & seasons to English abbreviations seems to really help the outputs with foreign months
    input_string = normalize_months_in_string(input_string)
    input_string = normalize_seasons_in_string(input_string)
    years = _find_years_all_with_duplicates(input_string)
    if years is None:
        return []
    # remove duplicate years
    years = _uniquify_years_list(years)
    # find first and last years
    years.sort()
    years = remove_unlikely_years(years)
    return years


def remove_unlikely_years(years):
    previous_year = 0
    new_years = []
    for year in years:
        if (year - 100) > previous_year:
            new_years = []
        new_years.append(year)
        previous_year = year
    return new_years


def check_for_valid_year(year):
    """Is this a valid year that we can check against?"""
    try:
        year = int(year)
    except (ValueError, TypeError):
        return False
    current_year = datetime.datetime.now().year
    if 1600 <= year <= current_year:
        return True
    elif year == 9999:
        # Assume '9999' is legitimate year, meaning ongoing title
        return True
    return False


def make_valid_year_string(string):
    """take something like 1995/96 and return 1995/1996"""
    string = re.sub(" ", "", string)
    if re.match(r"\d\d\d\d", string):
        if len(string) == 4:
            return string
    else:
        return

    if re.match(r"\d\d\d\d\D+$", string):
        return
    m = re.search(r"(\d\d)(\d)(\d)(?:([-/])(\d{1,4}))?", string)
    if not m.group(5).isdigit():
        return
    if len(m.group(5)) == 3 or len(m.group(5)) > 4:
        return
    first_year = m.group(1) + m.group(2) + m.group(3)
    divider = m.group(4)
    second_year = None
    if len(m.group(5)) == 1:
        if int(m.group(5)) <= int(m.group(3)):
            return
        second_year = m.group(1) + m.group(2) + m.group(5)
    elif len(m.group(5)) == 2:
        decade = m.group(2) + m.group(3)
        if int(m.group(5)) <= int(decade):
            return
        second_year = m.group(1) + m.group(5)
    elif len(m.group(5)) == 4:
        if int(m.group(5)) < int(first_year):
            return
        second_year = m.group(5)
    if check_for_valid_year(first_year) and check_for_valid_year(second_year):
        out_string = first_year + divider + second_year
        return out_string


def find_missing_years_in_range(start, end, years_list):
    if type(years_list) != list:
        years_list = find_years_all(years_list)
    if not start or not end:
        return
    try:
        start = int(start)
        end = int(end)
    except ValueError:
        return

    if start > end:
        return

    current_year = datetime.datetime.now().year

    if end > current_year:
        end = current_year

    years_set = set()
    for year in years_list:
        years_set.add(int(year))
    missing_years_list = []
    y = start
    while y <= end:
        if y not in years_set:
            missing_years_list.append(y)
        y += 1
    return missing_years_list


def get_concatenated_year_range_between_two_dates(input_string, year_1, year_2):
    if not check_for_valid_year(year_1):
        year_1 = 1600
    if not check_for_valid_year(year_2):
        year_2 = 9999
    year_1 = int(year_1)
    year_2 = int(year_2)
    years_list = find_years_all(input_string)
    if not years_list:
        return ''
    valid_years_list = []
    for year in years_list:
        if int(year) < year_1 or int(year) > year_2:
            continue
        valid_years_list.append(year)
    concatenated = concatenate_years(valid_years_list)
    return concatenated


def get_concatenated_year_range(input_string):
    if len(input_string) < 4:
        return
    if not re.search(r"\d\d\d\d", input_string):
        return
    years_list = find_years_all(input_string)
    if years_list is not None and len(years_list) >= 1:
        concatenated = concatenate_years(years_list)
        return concatenated


def concatenate_years(input_list):
    if not input_list or len(input_list) < 1:
        return ''
    input_list.sort()
    if len(input_list) == 1:
        if check_for_valid_year(input_list[0]):
            return input_list[0]
        else:
            return
    last_year = None
    concat = None
    continue_flag = False

    for year in input_list:
        if check_for_valid_year(year) is False:
            continue
        if not concat:
            last_year = year
            concat = str(year)
            continue
        if year == (last_year + 1):
            continue_flag = True
            last_year = year
            continue
        if continue_flag is True:
            continue_flag = False
            concat += '-' + str(last_year)
        concat += ', ' + str(year)
        last_year = year
    if continue_flag is True:
        concat += '-' + str(last_year)
    return concat


def find_overlapping_years(range_1, range_2):
    """take two strings of years or ranges & return years that overlap"""

    years_1 = find_years_all(range_1)
    if len(years_1) == 0:
        return
    years_2 = find_years_all(range_2)
    if len(years_2) == 0:
        return

    common_years = []
    range_1_set = set(years_1)
    for y in years_2:
        if y in range_1_set:
            common_years.append(y)

    return common_years


def find_overlapping_year_range(range_1, range_2):
    """take two strings of years or ranges & return range of years from both"""

    years_list = find_overlapping_years(range_1, range_2)
    if len(years_list) == 0:
        return
    range_str = concatenate_years(years_list)
    return range_str


def find_nonoverlapping_years(range_1, range_2):
    """take two strings of years or ranges & return years from first not in second"""

    years_1 = find_years_all(range_1)
    if len(years_1) == 0:
        return
    years_2 = find_years_all(range_2)
    if len(years_2) == 0:
        return

    non_overlapping_years = []
    range_2_set = set(years_2)

    for y in years_1:
        if y not in range_2_set:
            non_overlapping_years.append(y)

    return non_overlapping_years


def find_nonoverlapping_year_range(range_1, range_2):
    """take two strings of years or ranges & return range of years from first not in second"""

    years_list = find_nonoverlapping_years(range_1, range_2)
    if len(years_list) == 0:
        return
    range_str = concatenate_years(years_list)
    return range_str


# ------------------------------------------------------------------------------
#   INTERNAL UTILITY SUBROUTINES
# ------------------------------------------------------------------------------


def _find_years_all_with_duplicates(input_string):
    """
    Find every year, and return all individual years in a range like (1848-1862)
    we will assume that a slash year (1943/1944) will return both/all years in slash

    Takes a string, attempts to extract years from it, and returns all years.
    """

    without_years_dict = {}
    years = []

    input_string = str(input_string)
    # Nothing resembling a year. Fail early.
    if not input_string or len(input_string) == 0 or not re.search(r"[12]\d\d\d", input_string):
        return years

    # easier to search if there's always a non-digit character outside of any search range.
    input_string = 'X ' + input_string + ' X'

    input_string = get_missing_years(input_string, without_years_dict)

    holdings = _year_cleaner(input_string)

    # to account for holdings rejected by the year cleaner
    if not holdings or not re.search(r"\d\d\d\d", holdings):
        # TODO: commented out warning log for now. Make it optional?.
        #  rejection tracking, for bug fixing
        # m = re.findall(r"(\d\d)\d\d", input_string)
        # for number_string in m:
        #     if 16 <= int(number_string) <= 20:
        #         log_out = open('dates_warning.log', 'a', encoding='utf8')
        #         log_out.write(input_string + "\n")
        #         log_out.close()
        return years

    # edge case: (no. 1620, 1622-1626, 1628, 1630-1631, 1633, 1635-1636)
    holdings = re.sub(r"\( *no\.[^)]*\)", "", holdings)

    # deal with things like this: 1999-00
    # convert them to reasonable dates & reinsert to be found later
    while True:
        m = re.search(r"((\D)(1[7-9])([1-9]\d)([/-])(0\d)(\D))", holdings)
        if m:
            original_string, pre_string, decade, first_years, divider, second_years, post_string = m.groups()
            second_decade = int(decade) + 1
            replacement_string = "{}{}{}{}{}{}{}".format(pre_string, decade, first_years, divider, second_decade, 
                                                         second_years, post_string)
            holdings = holdings.replace(original_string, replacement_string)
        else:
            break
        
    # find years like: 1823-46 or 1823/46
    # convert them to reasonable dates & reinsert to be found later
    while re.search(r"\D[12]\d\d\d[-/]\d\d\D", holdings):
        holdings = re.sub(r"(\D)([12]\d)(\d\d) ?([-/]) ?(\d\d\D)",
                          r"\1\2\3\4\2\5", holdings, count=1)

    # prep work to deal with slash years in a range: 1966/1967-1969/1970
    while re.search(r"- ?[12]\d\d\d/[12]\d\d\d(\D)", holdings):
        m = re.search(r"- ?([12]\d\d\d)/([12]\d\d\d)\D", holdings)
        y1, y2 = m.groups()
        holdings = re.sub(r"- ?([12]\d\d\d)/([12]\d\d\d)(\D)", "-\\2\\3", holdings, count=1)
        _range_adder(y1, y2, without_years_dict, years)

    while re.search(r"\D[12]\d\d\d/[12]\d\d\d-", holdings):
        m = re.search(r"\D([12]\d\d\d)/([12]\d\d\d)-", holdings)
        y1, y2 = m.groups()
        holdings = re.sub(r"(\D)([12]\d\d\d)/([12]\d\d\d)-",
                          "\\1\\2-", holdings, count=1)
        _range_adder(y1, y2, without_years_dict, years)

    # any years separated by a dash
    while re.search(r"\D[12]\d\d\d[^,;]*?-[^,;]*[12]\d\d\d\D", holdings):
        m = re.search(r"\D([12]\d\d\d)[^,;]*?-[^,;]*([12]\d\d\d)\D", holdings)
        y1, y2 = m.groups()
        holdings = re.sub(r"(\D)([12]\d\d\d)[^,;]*?-[^,;]*([12]\d\d\d)(\D)", "\\1; ;\\4", holdings, count=1)
        _range_adder(y1, y2, without_years_dict, years)

    # any years separated by a slash -- 1969/1970
    while re.search(r"\D[12]\d\d\d ?/ ?[12]\d\d\d\D", holdings):
        m = re.search(r"\D([12]\d\d\d) ?/ ?([12]\d\d\d)\D", holdings)
        y1, y2 = m.groups()
        holdings = re.sub(r"(\D)([12]\d\d\d) ?/ ?([12]\d\d\d)(\D)", "\\1 \\4", holdings, count=1)
        _range_adder(y1, y2, without_years_dict, years)

    open_year = find_open_year_ranges(holdings)
    if open_year is not None:
        current_year = datetime.datetime.now().year
        # for open ranges, we're arbitrarily subtracting a single year
        current_year -= 1
        _range_adder(open_year, current_year, without_years_dict, years)

    # find regular individual years
    while re.search(r"\D[12]\d\d\d\D", holdings):

        m = re.search(r"(\D)([12]\d\d\d)(\D)", holdings)
        y1 = m.group(2)
        holdings = re.sub(r"(\D)([12]\d\d\d)(\D)",
                          "\\1;;\\3", holdings, count=1)
        _year_adder(y1, without_years_dict, years)
    return years


def get_missing_years(input_string, without_years_dict):

    without_segments_list = []

    # EDGE CASE
    # deal with "1873-1877 (W/O 1874)" or "1873-1877 (Bd W/O 1874)" or "1873-1877 (lacks 1874)"
    bound_with_regex = r"\( ?(?:(?:bd\.?|bound) (?:w\.?\/o\.?|without)|lacks)([^\)]+)\)"
    while re.search(bound_with_regex, input_string, flags=re.I):
        m = re.search(bound_with_regex, input_string, flags=re.I)
        to_check = m.group(1)
        # we'll skip anything that isn't a full year, so skip anything that might indicate months or issue numbers
        if not re.search(r"[a-z]", to_check, flags=re.I):
            if ':' not in to_check and re.search(r"\d\d\d\d", to_check):
                without_segments_list.append(to_check)
        input_string = re.sub(bound_with_regex, " ", input_string, flags=re.I)

    # put parens around seen "lacks" statement where we can
    if "lack" in input_string.lower() and "(lack" not in input_string.lower() and ";" in input_string:
        input_string = re.sub(r"(\b)lack(?:s|ing)? *([^;]*)", r"\1 (lacks \2)", input_string, flags=re.I)

    lacks_regex = r"\(lacks?:? ([^\)]*)\)"
    while re.search(lacks_regex, input_string, flags=re.I):
        m = re.search(lacks_regex, input_string, flags=re.I)
        to_check = m.group(1)
        input_string = re.sub(
            lacks_regex, "", input_string, flags=re.I)
        # we'll skip anything that isn't a full year, so skip anything that might indicate months or issue numbers
        if not re.search(r"[:a-z]", to_check, flags=re.I):
            if re.search(r"\d\d\d\d", to_check, flags=re.I):
                without_segments_list.append(to_check)

    if len(without_segments_list) > 0:
        without = ' ; '.join(without_segments_list)
        missing_years_list = _find_years_all_with_duplicates(without)
        for y in missing_years_list:
            try:
                without_years_dict[y] += 1
            except KeyError:
                without_years_dict[y] = 1

    return input_string


def _year_cleaner(holdings):
    """subroutine for (maybe occasionally unnecessary) cleaning of holdings line"""

    years_regex = _get_standard_regexes("years")
    months_regex = _get_standard_regexes("months")
    current_year = datetime.datetime.now().year

    # find year for "current year" stuff, which we will arbitrarily set as *last* year
    high_year = datetime.datetime.now().year
    high_year -= 1
    # assume any break of three or more spaces, or a tab, represents a break
    holdings = re.sub(r" {3}", " ; ", holdings)
    holdings = re.sub(r"\t", " ; ", holdings)

    # clear obvious call numbers
    holdings = re.sub(r"^X [A-Z]-?\d+ +", 'X ', holdings, count=1)

    # make sure there's a space after every comma
    holdings = re.sub(", ?", ", ", holdings)

    # deal with holdings like "Ja-My03" or "Se-Nv 2002"
    holdings = _fix_two_character_months(holdings)

    # normalize various words to "v."
    holdings = _normalize_volumes(holdings)

    # normalize various words to "no."
    holdings = _normalize_numbers(holdings)

    # reversed year and month in parens -- "(1952,Mar)"
    holdings = re.sub(r"\( *({})[,;\s]+({}(?: *\d\d?)?) *\)".format(years_regex, months_regex), r"(\2 \1)", holdings)

    # make sure parens around clear dates like 1901:July 6-1908:Dec.30
    regex_year_month_day = r"(?:1[789]|20)\d\d:[A-Z][a-z]+\.? ?\d{1,2}"
    holdings = re.sub(r"(\D)({}(?: ?[/-] ?{})?)".format(regex_year_month_day, regex_year_month_day), r"\1(\2)", holdings)

    # hasn't been finding open ranges in angled brackets, so change them to parens
    holdings = re.sub('<({})- ?>'.format(years_regex), r'(\1- )', holdings)

    # preparatory re-spacing of things like Dec26,1885
    holdings = re.sub(r"([a-z]+)(\d{1,2}),(\d\d\d\d)", r"\1 \2, \3", holdings, count=0, flags=re.I)

    # more parentheses around clear dates, like in "v.5 Jul 1959 - v.140 Feb 1, 1977"
    if '(' not in holdings:
        holdings = re.sub(r" *({} \d\d?(?: *- *\d\d)?, {})(\b)".format(months_regex, years_regex), r" (\1)\2", holdings)

    # records with volumes for years & no years v.1976-v.2014; for 1800+ only
    # search only works without a space between "v." and number,
    # because space-date is seen as a potential freestanding date
    holdings = holdings.replace(" v. ", " v.")

    # check for presence of four digit volumes that clearly aren't years ("v.1342")
    # if such exist, remove *all* volumes, so something like "v.1234' v.1888" doesn't produce the year 1888 as output
    delete_vols = False
    all_vols = re.findall(r"v\.(\d\d\d\d)", holdings)
    for vol in all_vols:
        if int(vol) < 1620 or int(vol) > (current_year + 1):
            delete_vols = True

    if delete_vols:
        holdings = re.sub(r"v\.\d\d\d\d(?: *[-/] *\d\d\d\d)?", " ", holdings)

    if re.search(r"v\.(?:1[89]|20)\d\d(?:[/-](?:1[89]|20)\d\d)?", holdings):
        if not re.search(r"[(\s]\d\d\d\d\b", holdings):
            holdings = re.sub(r"v\.((?:1[89]|20)\d\d(?:[/-](?:1[89]|20)\d\d)?)", r" \1 ", holdings)
    # volumes for years with commas, like v.1989, 1991
    holdings = re.sub(r"v\.((?:1[89]|20)\d\d, (?:1[89]|20)\d\d[-/,\s])", r"\1", holdings)

    # special case: preserve year in something like no.209-211,213-216,218,220, 1995
    # this will come up with spaces after commas, but don't know of a way to successfully deal with it
    one_to_three_digits = r"\d\d?\d?"
    regex_part = r"(?:{0}(?:[-\/]{0})?,)+".format(one_to_three_digits)
    holdings = re.sub(r"(?:v|vol|no)\. ?{0}{1}(?:[-/]{1})?, +(\d\d\d\d)".format(regex_part, one_to_three_digits),
                      r" \1", holdings)

    # remove numbers from something like no.123-234, 1952
    holdings = re.sub(r"\W(?:v|vol|n|no|p|pp|pg|pt)\.? ?{0}(?: ?[-/] ?{0})?, (\d\d\d\d)".format(one_to_three_digits),
                      r"; \1", holdings, flags=re.I)

    # to avoid problems with the following regex, in cases like 1981:no.1-1985:no.3
    holdings = re.sub(r"(\d\d\d\d):nos?\.? ?{0} ?- ?(\d\d\d\d):nos?\.? ?{0}".format(one_to_three_digits),
                      r"(\1-\2)", holdings)

    # remove some obvious numbers, like 1982:no.1234-13423
    holdings = re.sub(r":nos?\.? ?\d+(?: ?[/-] ?\d+)?", " ", holdings)

    # comma after "v" for volume, as in "v.44(1997/1998)-v,63:no.4(2006:Feb.)."
    holdings = re.sub(r"([\s-]v), *(\d)", "\1v.\2", holdings)

    # things like "no. 1598-1612, 1614-1623"
    regex_part = r"(?:\d\d\d+(?: ?[-\/] ?\d\d\d+)?, *)+"
    holdings = re.sub(r"(\W)(?:n|no|v|vol|pt|p|pp|pg)\. ?{}\d\d\d+(?: ?[-/] ?\d\d\d+)?".format(regex_part), r"\1 ",
                      holdings)

    # delete vol. & no. strings that look sort of like years
    holdings = re.sub(r"\b(?:v|no|n|vol|p|pp|pg|pt)\.? ?\d\d\d\d+(?: ?[-/] ?\d\d(?:\d\d+)?)?", "  ", holdings, count=0,
                      flags=re.I)

    # start with fixing a specific issue -- 1974:no.1
    holdings = re.sub(r"(\d\d\d\d):(nos?\.?) ?(\d+)", r"\1 \2\3", holdings)
    # SPECIAL case -- v.42, no.4 (Special 1994)
    holdings = re.sub(r"special", "", holdings, count=0, flags=re.I)

    # get rid of things that are definitely not years
    holdings = re.sub(r"v\. ?\d+-v\. ?\d+", "", holdings)
    holdings = re.sub(r"v\. ?\d{1,3}- ?\d{1,3}\b", "", holdings)
    holdings = re.sub(r"\d+[r|n]d", "", holdings)
    holdings = re.sub(r"\d+th", "", holdings)
    holdings = re.sub(r"([^o])v(?:ol(?:ume)?)?\.? ?\d+(?:[:,]? ?no\.? ?\d+)? ?",
                      r"\1 ", holdings, count=0, flags=re.I)
    holdings = re.sub(r"(\d\d\d\d):N[or]\.? ?\d+", r"\1 ", holdings)
    # for 2004:Jan. and the like
    holdings = re.sub(r"(\d\d\d\d):[A-Za-z]+\.?", r"\1 ", holdings)
    holdings = re.sub(r"\b[a-z]\d+ ?- ?[a-z]\d+", " ", holdings,
                      count=0, flags=re.I)    # R8468-R8488
    holdings = re.sub(r"\b[a-z]\d+", " ", holdings, count=0,
                      flags=re.I)                 # R8488
    # clear out parens entirely taken up by a single vol or no expression -- (no.826-1123)
    vol_or_num = r"(?:v(?:ol)?)|(?:n(?:os?)?)\.?"
    vol_or_num_paren = r"(?:\( *v(?:ol)?)|(?:\( *n(?:os?)?)\.?"
    holdings = re.sub(r"{} *\d+(?: *[-/] *(?:{})? *\d+)?\)".format(vol_or_num_paren, vol_or_num), '()', holdings)
    # clear out month, day year expressions, in parens
    holdings = re.sub(r"\([A-Z]+\.? ?\d{1,2}(?:/\d{1,2})?, (\d\d\d\d)\)", r"(\1)", holdings, count=0, flags=re.I)

    # reel numbers
    holdings = re.sub(r"(\b)r(?:eel)?s?\.? ?\d+(?: ?- ?(?:r(eel)?\.?)? ?\d+)?", r"\1", holdings)

    # specific fixes for '& index' and '& suppl'
    holdings = re.sub(r" *(?:&|and) index\)", ")", holdings, flags=re.I)
    holdings = re.sub(r" *(?:&|and)(?: *cum\.?)? *indexe?s? ?(?:for (?:years?)? \d\d\d\d(?: ?[/-] ?\d\d\d?\d? *)?)?\)",
                      ")", holdings, flags=re.I)
    holdings = re.sub(r" *(?:&|and)(?: *cum\.?)? *indexe?s? \d+(?: ?- ?\d+ *)?\)", ")", holdings, flags=re.I)
    holdings = re.sub(r" *(?:&|and) suppl(?:ement)?s?\.? *\)", ")", holdings, flags=re.I)

    # try to clear out references to an index
    # 1920-1940 index
    holdings = re.sub(r"\d{4} ?- ?\d{4} index\D*[,;(]", " ", holdings, count=0, flags=re.I)
    holdings = re.sub(r"\d{4} ?- ?\d{4} index\D*$", " ", holdings, count=0, flags=re.I)
    # "index 1920-1940" or "index 1920-40"
    holdings = re.sub(r"index \d{4} ?- ?\d{2,4}", " ",
                      holdings, count=0, flags=re.I)
    holdings = re.sub(r"index ?\(\d{4} ?- ?\d{2,4}\)", " ", holdings, count=0, flags=re.I)

    # remove reference to new series of form "n.s.:"
    holdings = re.sub(r"n\. ?s\. ?:? ?", " ", holdings)

    # colons to spaces
    holdings = holdings.replace(":", " ")

    # remove parenthetical references to supplements, special, issues, etc.
    # also try to remove missing, etc in parens that have gotten this far
    # also bound notes
    holdings = re.sub(r"\([^)]*(?:suppl|special|index|appendi|missing|lack|without|bound|bind)[^)]*\)",
                      "  ", holdings, flags=re.I)
    # clear out things like  "no.2307-2335 (Apr 1988-Nov 1990)"
    # or "pp.2307-2335, 2345-2347, 2349-2355 (Apr 1988-Nov 1990)"
    long_digit_regex = r"\d+ ?(?: ?[-\/] ?\d+)?"

    holdings = re.sub(r"\b(?:no?\.?|p[pg]?\.?)? *{}(?:, ? ?\d+(?:, {}(?:, ?{}(?:, {})?)?)?)? *(\([^)]*\d\d\d\d)"
                      .format(long_digit_regex, long_digit_regex, long_digit_regex, long_digit_regex),
                      r"  \1", holdings, count=0, flags=re.I)

    # clear out parens with no digits
    holdings = re.sub(r"\([^)\d]+\)", " ", holdings)

    # clear out things like  "no.2014-2015 partially incomplete (1988)"
    holdings = re.sub(r"no\. ?\d+ ?(?:- ?\d+)? [^,;|(]*(\([^)]*)", r" \1", holdings, flags=re.I)

    # long string of no. followed by a date.
    # ex.: nos. 119-159, 277-516, 1764-1767, 1770-1866, 1970-2018, 2070-2116, 2623-2625, 2718-2759 (1909-1961)
    holdings = re.sub(r"nos?\. ?\d+[^(]* (\( ?\d\d\d\d(?: ?- ?\d\d+)? ?\))", r" \1", holdings, flags=re.I)
    holdings = re.sub(r"\bno\.? ?\d+ ?- ?\d+[,;]", "  ", holdings, count=0, flags=re.I)
    holdings = re.sub(r"\bno\.? ?\d+ ?- ?\d+ ?\((?:[A-Z][a-z]+\.? )?(\d{4}) ?- ?(?:[A-Z][a-z]+\.? )?(\d{4})\)",
                      r" \(\1-\2\)", holdings, count=0, flags=re.I)
    # this will eliminate numbers like "no.1975"
    holdings = re.sub(r"([^n]):?nos?\.? ?\d*", r" \1 ", holdings, count=0, flags=re.I)
    holdings = re.sub(r"[^n]num(?:ber)?s?\.? ?\d+", "", holdings, count=0, flags=re.I)
    holdings = re.sub(r" p[pg]?\.? ?\d+ ?- ?\d+", " ",  holdings, count=0, flags=re.I)
    holdings = re.sub(r"(\s,;-)p.? ?\d+ ?- ?\d+", r"\1 ",  holdings, count=0, flags=re.I)
    holdings = re.sub(r"^p.? ?\d+ ?- ?\d+", " ", holdings,
                      count=0, flags=re.I)
    # deals with pages. Leaving out "S" at the start so as to not block dates starting with "Sep"
    holdings = re.sub(r"([^Ss])[A-Za-z]p[gp]?s?\.? ?\d+", r"\1", holdings, count=0, flags=re.I)
    holdings = re.sub(r" p[pg]?\. ?\d+ ?(?:[-/] ?\d+)?", "",  holdings, count=0, flags=re.I)

    holdings = re.sub(r"pages? ?\d+ ?(?:[-/] ?\d+)?", "", holdings, count=0, flags=re.I)

    # TODO rationalize the pages parts

    # if it looks as though the year extends to the present, add the present close date
    # i.e., "2011-" becomes "2011-2015"
    # arbitrarily use *last* year
    holdings = re.sub(r"(\d\d\d\d)\)?- *$", r"\1-" + str(high_year), holdings)

    holdings = re.sub(r"(\d\d\d\d)\)?-;", r"\1-" + str(high_year) + ";", holdings)

    holdings = ';' + holdings + ';'

    if re.search(r"class", holdings, flags=re.I):
        holdings = re.sub(r"class ?(?:of )?'?\d+(?: ?[-/] ?'?\d+)?", " ", holdings, count=0, flags=re.I)

    # remove day numbers and commas in expressions with months and range
    # (Apr 2, 1926-Dec 20, 1952)
    holdings = re.sub(r"[A-Za-z]+\.? \d{1,2}(?:/\d{1,2})?, (\d\d\d\d) ?- ?", r" \1-", holdings, count=0, flags=re.I)
    holdings = re.sub(r" ?- ?[A-Za-z]+\.? \d{1,2}(?:/\d{1,2})?, (\d\d\d\d)", r"-\1 ", holdings, count=0, flags=re.I)

    # make sure there's space around the parentheses
    holdings = re.sub(r'\(', ' (', holdings)
    holdings = re.sub(r'\)', ') ', holdings)

    # colons mess things up for some reason
    holdings = re.sub(r":(\d\d\d\d)", r" \1", holdings)
    holdings = re.sub(r"(\d\d\d\d):", r"\1 ", holdings)
    holdings = re.sub(r":", ", ", holdings)
    # fix silly spacing issue
    holdings = re.sub(r"(\d\d\d\d)no\.", r"\1 no.", holdings)
    # # Sanity check for bad date range like '1881-1838'
    # # Lots of these will by typos, but we can't fix that
    # years_checking = re.findall(r"(\d\d\d\d)[^,;\d\d\d\d]*-[^,;]*(\d\d\d\d)", holdings)
    # print("Exiting year_cleaner: " + holdings)
    return holdings


# ---------------------------------------------------------------------------------------------------------------------
# PRIVATE SUBROUTINES
# ---------------------------------------------------------------------------------------------------------------------

def _uniquify_years_list(years_list):
    """List of years to sorted list of unique years"""
    return sorted(list(set(years_list)))


def _fix_two_character_months(holdings):
    """
    Deal with holdings like "Ja-My03" or "Se-Nv 2002"
    Will require either the dash or the month crammed against a year.
    """
    if re.search(r"[\s-][ADFJMNO][acegpvy](\d\d(?:\d\d)?)([\s-])", holdings):
        # fix year first
        m = re.search(r"[\s-]([ADFJMNO][acegpvy])(\d\d(?:\d\d)?)([\s-])", holdings)
        year = m.group(2)
        if int(year) < 99:
            if int(year) > 20:
                new_year = "19" + year
            else:
                new_year = "20" + year
            month = m.group(1)
            holdings = re.sub(month + year, month + " " + new_year, holdings)

    elif not not re.search(r" [ADFJMNO][acegpy]-[ADFJMNO][acegpvy] \d\d", holdings):
        pass
    else:
        return holdings
    short_months = {
        "Ja": "Jan",
        "Fe": "Feb",
        "Mr": "Mar",
        "Ap": "Apr",
        "My": "May",
        "Je": "June",
        "Jy": "July",
        "Ag": "Aug",
        "Se": "Sep",
        "Oc": "Oct",
        "Nv": "Nov",
        "De": "Dec"
    }
    for sm in short_months:
        holdings = holdings.replace(sm, short_months[sm])
    return holdings


def _years_missing(without_years_dict, without_segments_list):
    """
    deal with a parenthetical with something like "Bd W/O 1963"
    idea is that we'll make a hash of occurrences of these, each year with value equal to number of occurrences.
    then subtract 1 from hash value for each time we find that year as existing.
    if "without" value is 0 then allow year in output.
    so one "without" + two "withs" equals a useful output year.

    TODO: This subroutine currently isn't called anywhere. Needs to be tested (a lot) & incorporated.
    """

    # d_re = "\d\d\d\d"
    months_re = r"[Jan|Feb|Mar|Apr|May|June?|July?|Aug|Sept?|Oct|Nov|Dec|"
    months_re += r"[Ss]pring|[Ss]ummer|[Ff]all|[Aa]utumn|[Ww]inter]\.?"

    for segment in without_segments_list:
        # extra characters for spacing and detecting things at beginning/end of string
        segment = 'X ' + segment + ' X'

        # remove partial year segments (2006:3, 2001:Jan, and so on)
        while re.search(r"\d\d\d\d[:,][a-z0-9]+", segment, flags=re.I):
            segment = re.sub(r"\d\d\d\d[:,][a-z0-9]+", "", segment, flags=re.I)

        regex = months_re + " ?d_re"
        while re.search(regex, segment):
            segment = re.sub(regex, "", segment)

        # find years like: 1823-46 or 1823/46
        # convert them to reasonable dates & reinsert to be found later
        while re.search(r"\D\d\d\d\d[-/]\d\d\D", segment):
            segment = re.sub(r"(\D)(\d\d)(\d\d) ?([-/]) ?(\d\d\D)", r"\1\2\3\4\2\5", segment)

        # remove outer years when slash years are at end of range
        # example: 1892/1893-1898 -> 1893-1898
        # idea is that i 1892/1893 is missing, still 1891/1892 might be present
        while re.search(r"\d\d\d\d/\d\d\d\d ?-", segment):
            segment = re.sub(r"\d\d\d\d/(\d\d\d\d) ?-", r"\1-", segment)
        while re.search(r"- ?\d\d\d\d/\d\d\d\d", segment):
            segment = re.sub(r"- ?(\d\d\d\d)/\d\d\d\d", r"-\1", segment)

        # remove individual slash years, like this: 1846/1847
        # idea is that in range with lacking slash date, it will still have surrounding years
        # ex.: "1920-1930 (Bd w/o 1922/1923)" -- guess that it will have 1921/1922 & 1923/1924
        # CAN REMOVE THIS SECTION IF WE WANT TO BE CONSERVATIVE WITH WHAT WE KEEP IN
        segment = re.sub(r"\d\d\d\d/\d\d\d\d", " ", segment)

        # after all this cleaning, collect missing years & put them in the hash
        missing_years_list = find_years_all(segment)

        for year in missing_years_list:
            try:
                without_years_dict[year] += 1
            except KeyError:
                without_years_dict[year] = 1


def _year_adder(year, without_years_dict, years):
    """add years to find_years_all year array"""
    try:
        year = int(year)
    except ValueError:
        return
    if check_for_valid_year(year) is False:
        return

    if year in without_years_dict and without_years_dict[year] >= 1:
        without_years_dict[year] -= 1
        return

    years.append(year)


def _range_adder(start_year, end_year, without_years_dict, years):
    """add range of years to list of years"""
    try:
        start_year = int(start_year)
        end_year = int(end_year)
    except ValueError:
        return
    if check_for_valid_year(start_year) is False or check_for_valid_year(end_year) is False:
        return
    if start_year > end_year:
        return
    y = start_year
    while y <= end_year:
        _year_adder(y, without_years_dict, years)
        y += 1


def _normalize_volumes(holdings):
    """
    A list of words that can generally be normalized to "v."
    Taken from the normalizer.
    """
    vol_words = [
        "aa?rg",
        "aargang",
        "ann?[io]",
        "ann[ée]e",
        "anul",
        "ausg",
        "ar",
        "band",
        "bd",
        "b(?:oo)?k",
        "cilt",
        "dil",
        "deel",
        "etos",
        "evf",
        "fase",
        "g",
        "god",
        "ja[ah]rg?(?:ang)?",
        "jg",
        "k",
        "kerekh",
        "kn",
        "knj(?:iga)?",
        "kot(?:et)?",
        "letnik",
        r"lfg\.? *",
        "livre?",
        "memoir",
        "(?:al-)?mujallad",
        "roc",
        "roc[nz]",
        "rocnik",
        "rok",
        "(?:al-)?sanah",
        "sefer",
        "sene",
        "sb",
        "sbornik",
        "sv[ae]zek",
        "t",
        "tom[eo]?",
        "tomu[ls]",
        "v",
        r"v\.r\.",
        "vol",
        "vol_s",
        "volumes?",
        "vyp",
        "z"
    ]
    vol_regex = '(?:' + '|'.join(vol_words) + ')'

    holdings = re.sub(r"(\b){}\.?(\b)".format(vol_regex), r"\1v.\2", holdings, flags=re.I)
    # reverse things like "11.v. 1996" that can result from "111.Jahr 1996"
    holdings = re.sub(r"(\b)(\d\d?\d?)\.?v\.", r"\1v.\2", holdings)
    # cleanup of nonsensical "v.-v." that can result from something like "Part K-Z 1995"
    holdings = re.sub(r" v\.-v\. ", " ", holdings)
    return holdings


def _normalize_numbers(holdings):
    """
    A list of words that can generally be normzlized to "no."
    Taken from the normalizer.
    """
    number_words = [
        "abt",
        "(?:al-ʻ)?adad",
        "br",
        "broj",
        "cis(?:lo)?",
        "czesc",
        "fasc",
        "fic",
        "fuz(?:et)?",
        "gil",
        "h",
        "he?fte?",
        "hov",
        "iss(?:ue)?",
        "kniga",
        "lief(?:erung)?",
        "nide",
        "no",
        "nos",
        "noum",  # "nøum."
        "nr",
        "sayi",
        r"sa\.",
        r"sem(?:est(?:er|re))?\.?",
        r"sz\.",
        "teuch",
        "trimest(?:er|re)",
        "zesz(?:yty?)?",
    ]

    number_regex = '(?:' + '|'.join(number_words) + ')'

    holdings = re.sub(r"(\b){}\.?(\b)".format(number_regex), r"\1no.\2", holdings, flags=re.I)
    holdings = holdings.replace("no..", "no.")
    return holdings


def _get_standard_regexes(wanted_regex):
    regexes = {
        "years": r"(?:1[6789]\d\d|20[01]\d)(?: *[-\/] *(?:1[6789]\d\d|20[01]\d))?",
        "months": r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Spring|Summer|Fall|Winter])"
    }
    try:
        return regexes[wanted_regex]
    except KeyError:
        sys.exit("Bad regex request? Requested regex is {}".format(wanted_regex))


if __name__ == "__main__":
    """
    Testing section.
    """
    parser = argparse.ArgumentParser(description="Checks and tests for year utilities suite.")
    parser.add_argument("string_to_check", help="String to check.", type=str)
    args = parser.parse_args()
    print("input:\t{}".format(args.string_to_check))
    print("concat:\t{}".format(get_concatenated_year_range(args.string_to_check)))
