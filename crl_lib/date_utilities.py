import datetime


def get_month_name_from_number(n):
    """
    Get the month abbreviation from a month number.
    """
    try:
        n = int(n)
    except ValueError:
        raise ValueError("Month check failed; integer not input.")
    
    numbers_to_month_dict = get_number_to_month_dict()

    try:
        return numbers_to_month_dict[n]
    except KeyError:
        raise KeyError("Invalid month number: {}".format(n))
    

def get_number_to_month_dict():
    """
    Dict of numbers to month abbreviations, with numbers as ints.
    """
    num_to_month = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May',
        6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep',  10: 'Oct',
        11: 'Nov', 12: 'Dec'}
    return num_to_month


def get_current_year():
    """Wrapper for datetime.datetime.now().year"""
    import datetime
    return datetime.datetime.now().year


def get_today_string(separator_character=""):
    """
    Return a string in the form "YYYYMMDD", such as "20190309".

    By passing a separator character, the output can be turned into something
    like "2019-03-09". Example:

        today = get_today_string(separator_character='-')
        identical_today = get_today_string('-')

    """
    return datetime.datetime.now().strftime("%Y{0}%m{0}%d".format(separator_character))
    

def marc_year_to_year(year, u_digit=5):
    """
    Takes a year from the MARC 008 and tries to normalize it a bit.
    Change u in start & end year to digit (default is 5); i.e., 192u-193u -> 1925-1935.
    Assume we can only repair trailing 'u'; '19uu' shoud fail.
    Not checking for "reasonable" years, becase monographs (especially microfilm) can have "unreasonable" years of before 1600.
    """
    if len(str(year)) != 4:
        return None
    year = str(year)
    year = year.replace("u", str(u_digit))
    if year.isdigit():
        return year
    else:
        return None


def check_year_between(start_year, end_year, found_year):
    """Is a year between two other years?
    Assume if year equals start or end year it's OK.
    Returns None on "nonsensical" or "can't check" errors;
    can't check examples: - found_year is '19uu'
                          - start/end years are out of order
                          - non-sensical dates like 1273 or 9151
    """
    # specifically to reject found year with 'u' characters
    try:
        found_year = int(found_year)
    except ValueError:
        return None
    except TypeError:
        return None

    # remove 'u' characters from start/end years
    # using most conservative estimates -- 195u start year becomes 1950
    start_year = marc_year_to_year(start_year, 0)
    end_year = marc_year_to_year(end_year, 9)

    # even with nonsensical years or out-of-order years or other issues, a 
    # given value that matches a start or end date is valid
    if str(found_year) == str(start_year) or str(found_year) == str(end_year):
        return True

    if start_year is None or end_year is None:
        return None

    # nonsensical years anywhere invalidate the check
    if check_for_reasonable_year(start_year, end_year, found_year) is False:
        return None

    start_year = int(start_year)
    end_year = int(end_year)
    found_year = int(found_year)

    # 9999 is valid in MARC 008 dates, but not in found_year
    if found_year == 9999:
        return None

    # out-of-order dates; something's wrong
    if start_year > end_year:
        return None

    if (found_year >= start_year) and (found_year <= end_year):
        return True

    return False


def check_full_range_between(start_year, end_year, found_start, found_end):
    """Is a range of years contained within another range of years?
    Assume if year equals start or end year it's OK.
    'None' response means bad entry or dates we can't check (typos, etc)
    """

    start = check_year_between(start_year, end_year, found_start)
    end = check_year_between(start_year, end_year, found_end)

    if start is True and end is True:
        return True
    if start is False or end is False:
        return False
    return None


def check_start_year(given_year, found_year):
    """
    Check found year against given start date of range.
    Returns True if found year comes after given year.
    Returns False if found year before given year.
    Returns None if found or given year aren't years.
    """
    try:
        found_year = int(found_year)
    except ValueError:
        return None
    except TypeError:
        return None
    given_year = marc_year_to_year(given_year)
    found_year = marc_year_to_year(found_year)

    if not given_year or not found_year or found_year == 9999:
        return None

    if found_year < given_year:
        return False
    return True


def check_end_year(given_year, found_year):
    """
    Check found year against given year at end of range.
    Returns True if found year comes before given year.
    Returns False if found year comes after given year.
    Returns None if found or given years aren't years.
    """
    try:
        found_year = int(found_year)
    except ValueError:
        return None
    except TypeError:
        return None

    given_year = marc_year_to_year(given_year)
    found_year = marc_year_to_year(found_year)

    if not given_year or not found_year or found_year == 9999:
        return None

    if found_year > given_year:
        return False
    return True


def return_earlier_year(year_a, year_b):
    """
    Compare two years and returns earlier.
    If only one is valid year, returns it.
    Returns None on two invalid years.
    """
    year_a = marc_year_to_year(year_a)
    year_b = marc_year_to_year(year_b)
    if check_for_reasonable_year(year_a) is True:
        if check_for_reasonable_year(year_b) is True:
            if year_a < year_b:
                return year_a
            else:
                return year_b
        else:
            return year_a
    elif check_for_reasonable_year(year_b) is True:
        return year_b
    return ''


def return_later_year(year_a, year_b):
    """
    Compare two years and returns later.
    If only one is valid year, returns it.
    Returns None on two invalid years.
    """
    year_a = marc_year_to_year(year_a)
    year_b = marc_year_to_year(year_b)
    if check_for_reasonable_year(year_a) is True:
        if check_for_reasonable_year(year_b) is True:
            if year_a > year_b:
                return year_a
            else:
                return year_b
        else:
            return year_a
    elif check_for_reasonable_year(year_b) is True:
        return year_b
    return ''


def check_for_reasonable_year(*years):
    """
    Returns True on reasonable year, False on "unreasonable" number, None on non-number.
    "Reasonable year" means four digits between 1600 and current year, or "date" of 9999.
    1605 is first ever European newspaper, so use 1600 date.
    """
    now = get_current_year()
    now += 1
    for year in years:
        try:
            year = int(year)
        except ValueError:
            return None
        except TypeError:
            return None
    if (year < 1600) or ((year > now) and (year != 9999)):
        return False
    return True
