"""
Tools to attempt to pull month and date strings out of text.
This is very much a work in progress, and much of it will not work.
At the moment it is most useful for normalizing, using the functions
normalize_months_in_string and normalize_seasons_in_string. These will
normalized English and many foreign months and month abbreviations to "Jan",
"Feb", "Mar", etc., and English and many foreign seasons words and
abbreviations to "Spring", "Summer", "Fall", and "Winter".

A full normalizing routine would be as follow:

    from months_finder import normalize_months_in_string, normalize_seasons_in_string

    string_with_normalized_months = normalize_months_in_string(original_string)
    fully_normalized_string = normalize_seasons_in_string(string_with_normalized_months)

Beyond unpredictable misspellings and non-standard abbreviations, known months that are
in covered languages that generally don't work are:
    * "list" (Czech abbreviation for November)
    * "ún" (Czech abbreviation for February; works in Unicode version, not as "un")
    * "set" (Possible Spanish & Portuguese abbreviation for September; this is partially covered)

Some covered languages won't have their own subroutines because I don't want to duplicate entries.
These languages currently are: Swahili
"""

import re
import unidecode

# TODO: this is a straight port from an old Perl script, and not everything works.


# ----------------------------------------------------------------------
# Main subroutines
# ----------------------------------------------------------------------

def make_months_years_days_regex():
    """Regex to find months with days and years. Not completely functional"""
    months_expression = _make_months_regex_string()

    date = r"\b[0-3]?[0-9]\b"
    year = _make_year_match_regex()
    expression = r'(? *{} ?'.format(months_expression)
    expression += date
    expression += r'(?: ?[-/] ?{})?'.format(date)   # optional second date -- Oct 23/24, OR
    expression += r'(?: ?(?:-|/|to) ?'     # optional second month/date -- Oct 23-Nov 8
    expression += months_expression
    expression += r' ?' + date
    expression += r'(?: ?[-/] ?{})?'.format(date)  # optional second date on second expression -- Oct 3-Nov 4/5
    expression += r')?'                        # end optional second date
    expression += r',? ?'
    expression += year
    # Notes/TODO:
    # 21 Oct, 1986    --> think can't do these, collision with "vol 21 Oct, 1986"
    # 21-24 Oct, 1986 --> see note above
    return expression


def make_months_years_regex():
    """Regex to find months and years. Not entirely functional."""
    months_expression = _make_months_regex_string()
    year = _make_year_match_regex()
    expression = r'(? *' + months_expression
    expression += r'(?: (?:de) )?'      # "Diciembre de 1849"
    expression += r'(?: ?(?:-|/|to|and|et|a|și) ?'  # și = "and" in Romanian
    expression += months_expression
    expression += r')?(?:\.|,)?'     # have seen dates like "October. 2010"
    expression += r' ?' + year
    return expression


def make_inverse_months_years_regex():
    """
    Regex to find months coming after the year, as in 1857 April-May.
    Not complerely functional.
    """
    months_expression = _make_months_regex_string()
    year = _make_year_match_regex()
    expression = r'(? *{} ?'.format(year)
    expression += months_expression
    expression += r'(?: ?(?:-|/|to|and|et|a|și) ?'  # și = "and" in Romanian
    expression += months_expression
    expression += r')?,?'
    return expression


def make_months_seasons_years_regex():
    """Regex to find months & seasons with years. Not completely functional."""
    months_expression = _make_months_regex_string()
    year = _make_year_match_regex()
    expression = r'(? *{0}(?: ?(?:-|/|to) ?{0})?,?'.format(months_expression)
    expression += r' ?' + year
    return expression


def make_months_regex():
    """Regex to find strings that look like months."""
    expression = _make_months_regex_string()
    return expression


def make_months_seasons_regex():
    """Regex for finding months and seasons. Undertested."""
    expression = _make_months_seasons_regex_string()
    return expression


def make_seasons_regex():
    """Regex to find strings that look like seasons."""
    expression = _make_seasons_regex_string()
    return expression


def make_seasons_years_regex():
    seasons_expression = _make_seasons_regex_string()
    year = _make_year_match_regex()
    expression = seasons_expression
    expression += r'(?: (?:de|del|of) )?'  # "Fall of 1983"
    expression += r'(?: ?[/\-–] ?'
    expression += seasons_expression
    expression += r')?,?'
    expression += r' ?' + year
    return expression


def normalize_months_in_string(string):
    """
    Finds English and foreign months in a string and converts them to English abbreviations (Jan, Feb, Mar, etc.)
    Usage:

        normalized_string = normalize_months_in_string(original_string)

    """
    months = re.findall(r"(\w+)\.?", string)
    months_seen = set()
    for month in months:
        if month in months_seen:
            continue
        months_seen.add(month)
        new_month = get_month_name_from_name(month)
        if new_month:
            string = re.sub(month, new_month, string)
            string = re.sub(r"{}\.([-/)(\[\]])".format(new_month), r"{}\1".format(new_month), string)
            string = re.sub(r"{}\. *".format(new_month), new_month + " ", string)
    if "set" in string.lower():
        string = _set_month_finder(string)
    return string


def tokenize_months_in_string(string):
    """
    All months converted to the token '%MONTH%'
    This is for an experimental future general normalizer, and so is likely of limited use.
    """
    months = re.findall(r"(\w+)\.?", string)
    months_seen = set()
    for month in months:
        if month in months_seen:
            continue
        months_seen.add(month)
        new_month = get_month_name_from_name(month)
        if new_month:
            new_month = r'%MONTH%'
            string = re.sub(month, new_month, string)
            string = re.sub(r"{}\.([-/)(\[\]])".format(new_month), r"{}\1".format(new_month), string)
            string = re.sub(r"{}\. *".format(new_month), r"{} ".format(new_month), string)
    if "set" in string.lower():
        string = _set_month_finder(string)
    return string


def _set_month_finder(string):
    """
    Attempts to deal with the word "Set", which can mean "September" but can also appear in a lot of holdings statements
    as an English word.
    This is under tested, and likely misses a lot of cases.
    """
    # TODO: Spanish/Portuguese "Set" for Spetember is not current checked, because of clash with English word
    year_regex = r"(?:[16789]\d\d|20\d\d)"
    month_regex = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
    if re.search(r"set\.? *[-/] *{}".format(month_regex), string, flags=re.I):
        string = re.sub(r"set\.?", r"Sep", string, flags=re.I)
    elif re.search(r"{} *[-/] *set\.?".format(month_regex), string, flags=re.I):
        string = re.sub(r"set\.?", r"Sep", string, flags=re.I)
    elif re.search(r"set\.? *?{}".format(year_regex), string):
        string = re.sub(r"set\.?", r"Sep", string, flags=re.I)
    # TODO: Something like "Set 21, 1988" -- how to differentiate a set from September?
    return string


def normalize_seasons_in_string(string):
    """
    Takes a string and returns foreighn & English seasons normalized to Spring, Summer, Fall, or Winter.
    Usage:

        normalized_string = normalize_seasons_in_string(original_string)

    """
    seasons = re.findall(r"(\w+)", string)
    # "%CRLDMY%" is so that "Spr 1992-Spring 1994" won't become "Spring 1992-Springing 1994"
    string = re.sub(r"(\w+)", r"%CRLDMY%\1%CRLDMY%", string)
    seen_seasons = set()
    for season in seasons:
        if season in seen_seasons:
            continue
        seen_seasons.add(season)
        new_season = get_season_name_from_name(season)
        if new_season:
            string = string.replace(r"%CRLDMY%{}%CRLDMY%".format(season), new_season)
            string = re.sub(r"{}\.([-/)(\[\]])".format(new_season), new_season + r"\1", string)
            string = re.sub(r"{}\. *".format(new_season), r"{} ".format(new_season), string)
    string = string.replace(r"%CRLDMY%", r"")
    return string


def tokenize_seasons_in_string(string):
    """
    All seasons converted to the token '%MONTH%'
    (For normalization purposes, months & seasons are mostly interchangeable)
    This is for an experimental future normalizer and so is likely of limited current interest.
    """
    seasons = re.findall(r"(\w+)", string)
    # "%CRLDMY%" is so that "Spr 1992-Spring 1994" won't become "Spring 1992-Springing 1994"
    string = re.sub(r"(\w+)", r"%CRLDMY%\1%CRLDMY%", string)
    seen_seasons = set()
    for season in seasons:
        if season in seen_seasons:
            continue
        seen_seasons.add(season)
        new_season = get_season_name_from_name(season)
        if new_season:
            new_season = r'%MONTH%'
            string = string.replace(r"%CRLDMY%{}%CRLDMY%".format(season), new_season)
            string = re.sub(r"{}\.([-/)(\[\]])".format(new_season), new_season + r"\1", string)
            string = re.sub(r"{}\. *".format(new_season), "{} ".format(new_season), string)
    string = string.replace("%CRLDMY%", "")
    return string


def get_season_name_from_name(season):
    if not season:
        return
    number = _season_number_returner(season)
    if not number:
        return
    name = get_season_name_from_number(number)
    if name:
        return name


def get_season_name_from_number(number):
    """
   Convert seasons from number to name. This is mainly a part of the normalization process.
    """
    try:
        number = int(number)
    except ValueError:
        return
    if number == 1:
        return "Spring"
    elif number == 2:
        return "Summer"
    elif number == 3:
        return "Fall"
    elif number == 4:
        return "Winter"


def get_month_name_from_name(month):
    """
    Get a month abbreviation from any name. This is mainly a part of the normalization process.
    """
    num = _month_number_returner(month)
    if not num:
        return
    m = get_month_name_from_number(num)
    return m


def get_month_name_from_number(number):
    """
    Get a month abbreviation from a number. This is mainly a part of the normalization process.
    """
    try:
        number = int(number)
    except ValueError:
        return
    if number < 1 or number > 12:
        return
    months_key = get_months_key()
    return months_key[number]


def get_months_key():
    """
    Part of the normalization process.
    """
    months_key = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct",
                  11: "Nov", 12: "Dec"}
    return months_key


def get_months_with_abbrevs():
    """
    Part of the normaliation process.
    """
    months = get_foreign_months()
    abbrevs = get_foreign_months_abbreviations()
    for abbrev in abbrevs:
        months[abbrev] = abbrevs[abbrev]
    return months

# ---------------------------------------------------------------------------------------------------------------------


def get_foreign_months(unicode_ok=True):
    all_months = {}
    _months_to_hash_ref(all_months)
    if unicode_ok:
        return all_months
    _remove_unicode_keys_and_values(all_months)
    return all_months


def get_foreign_months_seasons(unicode_ok=True):
    all_months_seasons = {}
    _months_to_hash_ref(all_months_seasons)
    _get_seasons(all_months_seasons)
    if unicode_ok:
        return all_months_seasons
    _remove_unicode_keys_and_values(all_months_seasons)
    return all_months_seasons


def get_foreign_months_list():
    foreign_months = get_foreign_months()
    return sorted(list(foreign_months))


def get_foreign_months_seasons_list():
    foreign_months_seasons = get_foreign_months_seasons()
    return sorted(list(foreign_months_seasons))


def get_foreign_months_abbreviations(unicode_ok=True):
    abbrevs = {}
    _get_big_abbreviations_dict(abbrevs)
    _get_unknown_abbreviations(abbrevs)
    if not unicode_ok:
        _remove_unicode_keys_and_values(abbrevs)
    return abbrevs


def get_foreign_months_abbreviations_list():
    foreign_months_abbreviations = get_foreign_months_abbreviations()
    return sorted(list(foreign_months_abbreviations))

# ---------------------------------------------------------------------------------------------------------------------
# Internal Utilities
# ---------------------------------------------------------------------------------------------------------------------


def _dashes():
    dashes = '(?:–|—|-|--)'
    return dashes


def _months_to_hash_ref(all_ref):
    _get_arabic_months(all_ref)
    _get_czech_months(all_ref)
    _get_english_months(all_ref)
    _get_french_months(all_ref)
    _get_dutch_months(all_ref)
    _get_finnish_months(all_ref)
    _get_german_months(all_ref)
    _get_greek_months(all_ref)
    _get_hebrew_months(all_ref)
    _get_irish_months(all_ref)
    _get_italian_months(all_ref)
    _get_polish_months(all_ref)
    _get_portuguese_months(all_ref)
    _get_romanian_months(all_ref)
    _get_russian_months(all_ref)
    _get_spanish_months(all_ref)
    _get_thai_months(all_ref)
    _get_turkish_months(all_ref)
    _get_various_months(all_ref)


def _remove_unicode_keys_and_values(my_dict):
    for k in my_dict:
        new = unidecode.unidecode(k)
        try:
            val = unidecode.unidecode(my_dict[k])
        except AttributeError:
            val = my_dict[k]
        if new != k:
            my_dict[new] = val
            if "'" in new:
                new = new.replace("'", "")
                my_dict[new] = val
            my_dict.pop(k)


def _make_year_match_regex():
    regex = r'\(?'                      # optional open paren
    regex += r'\b(?:19\d\d|20[012]\d)'            # year proper
    regex += r'(?:/\d\d(?:\d\d)?)?\b'  # optional second year
    regex += r'\)?'                     # optional closing bracket
    return regex


def _make_months_regex_string():
    months = get_foreign_months()
    abbrevs = get_foreign_months_abbreviations()
    months_list = sorted(list(months))
    abbrevs_list = sorted(list(abbrevs))
    months_expression = r'\b|\b'.join(months_list) + r'\b'
    abbrevs_expression = r'(?:\.|\b)|\b'.join(abbrevs_list)
    expression = r'(?:(?:\b' + months_expression
    expression += r'\b)|(?:\b{}(?:\.|\b)))'.format(abbrevs_expression)
    return expression


def _make_seasons_regex_string():
    seasons = {}
    _get_seasons(seasons)
    seasons_list = sorted(list(seasons))
    seasons_expression = r'\b|\b'.join(seasons_list) + r'\b'
    seasons_expression = r'(?:\b' + seasons_expression + r'\b)'
    return seasons_expression


def _make_months_seasons_regex_string():
    months = get_foreign_months_seasons()
    abbrevs = get_foreign_months_abbreviations()
    months_list = sorted(list(months))
    abbrevs_list = sorted(list(abbrevs))
    months_expression = r'\b|\b'.join(months_list) + r'\b'
    abbrevs_expression = r'(?:\.|\b)|\b'.join(abbrevs_list)
    expression = r'(?:(?:\b' + months_expression + r'\b)|(?:\b'
    expression += abbrevs_expression + r'(?:\.|\b)))'
    return expression

# ---------------------------------------------------------------------------------------------------------------------
# Seasons
# ---------------------------------------------------------------------------------------------------------------------


def _get_seasons(hash_ref):
    # numbers are arbitrary -- should winter be 1 or 4?
    hash_ref['spring'] = 1
    hash_ref['summer'] = 2
    hash_ref['autumn'] = 3
    hash_ref['fall'] = 3
    hash_ref['winter'] = 4
    # abbreviations. TODO: make sure these  work without bad side effects
    hash_ref['spr'] = 1
    hash_ref['summ'] = 2
    hash_ref['sum'] = 2
    hash_ref['aut'] = 3
    hash_ref['win'] = 4
    hash_ref['wtr'] = 4
    hash_ref['wint'] = 4
    # Hebrew
    hash_ref['אָבִיב'] = 1
    hash_ref['aviv'] = 1
    hash_ref['קַיִץ'] = 2
    hash_ref['ka-itz'] = 2
    hash_ref['סְתָיו'] = 3
    hash_ref['stav'] = 3
    hash_ref['חֹורֶף'] = 4
    hash_ref['horef'] = 4
    # French
    hash_ref['printemps'] = 1
    hash_ref['été'] = 2
    hash_ref['ete'] = 2
    hash_ref['ete'] = 2
    hash_ref['automne'] = 3
    hash_ref['hiver'] = 4
    # German
    hash_ref['frühling'] = 1
    hash_ref['fruhling'] = 1
    hash_ref['fryhling'] = 1  # Swiss German
    hash_ref['sommer'] = 2
    hash_ref['herbst'] = 3
    hash_ref['härbscht'] = 3  # Swiss German
    hash_ref['harbscht'] = 3  # Swiss German
    # Greek
    hash_ref['άνοιξη'] = 1
    hash_ref['ánoiksē'] = 1
    hash_ref['anoikse'] = 1
    hash_ref['καλοκαίρι'] = 2
    hash_ref['kalokaíri'] = 2
    hash_ref['kalokairi'] = 2
    hash_ref['φθινόπωρο'] = 3
    hash_ref['phthinópōro'] = 3
    hash_ref['phthinoporo'] = 3
    hash_ref['χειμώνας'] = 4
    hash_ref['heimṓnas'] = 4
    hash_ref['heimonas'] = 4
    # Irish
    hash_ref['earrach'] = 1
    hash_ref['samhradh'] = 2
    hash_ref['fómhar'] = 3
    hash_ref['fomhar'] = 3
    hash_ref['geimhreadh'] = 4
    # Italian
    hash_ref['primavera'] = 1
    hash_ref['estate'] = 2
    hash_ref['autunno'] = 3
    hash_ref['inverno'] = 4
    # persian
    hash_ref['bahâr'] = 1
    hash_ref['bahar'] = 1
    hash_ref['tab\'stan'] = 2
    hash_ref['tāb\'stān'] = 2
    hash_ref['payîz'] = 3
    hash_ref['payiz'] = 3
    hash_ref['zemestān'] = 4
    hash_ref['zemestan'] = 4
    # Russian
    hash_ref['весна'] = 1
    hash_ref['vesna'] = 1
    hash_ref['vesna'] = 1
    hash_ref['лето'] = 2
    hash_ref['leto'] = 2
    hash_ref['leto'] = 2
    hash_ref['осень'] = 3
    hash_ref['osen\''] = 3
    hash_ref['osen'] = 3
    hash_ref['osen'] = 3
    hash_ref['зима'] = 4
    hash_ref['zima'] = 4
    hash_ref['zima'] = 4
    # polish
    hash_ref['wiosna'] = 1
    hash_ref['lato'] = 2
    hash_ref['jesień'] = 3
    hash_ref['jesien'] = 3
    hash_ref['jesien'] = 3
    # spanish
    hash_ref['verano'] = 2
    hash_ref['verán'] = 2  # Galician
    hash_ref['veran'] = 2  # Galician
    hash_ref['veran'] = 2  # Galician
    hash_ref['otoño'] = 3
    hash_ref['otono'] = 3
    hash_ref['otono'] = 3
    hash_ref['outono'] = 3  # Galician
    hash_ref['invierno'] = 4
    # turkish
    hash_ref['ilkbahar'] = 1
    hash_ref['yaz'] = 2
    hash_ref['sonbahar'] = 3
    hash_ref['kış'] = 4
    hash_ref['kıs'] = 4

    # various -- typos, misspellings, etc
    hash_ref['fal'] = 3

# ----------------------------------------------------------------------
# Abbreviations subroutines
# ----------------------------------------------------------------------


def _get_big_abbreviations_dict(hash_ref):
    """Much of this abbreviations list was taken from a page at Cataloging @ Yale
    (https://web.library.yale.edu/cataloging/months).

    Languages from that page are:

    English, Belorusian, Bosnian, Bulgarian, Croatian, Czech, Danish, Dutch, Estonian, French, German, Greek, Modern,
    Hungarian, Indonesian, Italian, Latin, Latvian, Lithuanian, Malaysian, Norwegian, Polish, Portuguese, Romanian,
    Russian, Serbian, Slovak, Slovenian, Spanish, Swedish, Turkish, Ukranian, Welsh
    """
    hash_ref['djan'] = 1
    hash_ref['enero'] = 1
    hash_ref['gen'] = 1
    hash_ref['genn'] = 1
    hash_ref['ian'] = 1
    hash_ref['ianv'] = 1
    hash_ref['ion'] = 1
    hash_ref['jaan'] = 1
    hash_ref['jan'] = 1
    hash_ref['jann'] = 1
    hash_ref['janv'] = 1
    hash_ref['jän'] = 1
    hash_ref['jänn'] = 1
    hash_ref['l\'ad'] = 1
    hash_ref['led'] = 1
    hash_ref['ocak'] = 1
    hash_ref['pros'] = 1
    hash_ref['saus'] = 1
    hash_ref['sich'] = 1
    hash_ref['sijec'] = 1
    hash_ref['studz'] = 1
    hash_ref['stycz'] = 1
    hash_ref['ιαν'] = 1
    hash_ref['chwef'] = 2
    hash_ref['feb'] = 2
    hash_ref['febb'] = 2
    hash_ref['febbr'] = 2
    hash_ref['febr'] = 2
    hash_ref['fev'] = 2
    hash_ref['fevr'] = 2
    hash_ref['févr'] = 2
    hash_ref['liut'] = 2
    hash_ref['luty'] = 2
    hash_ref['peb'] = 2
    hash_ref['phevr'] = 2
    hash_ref['subat'] = 2
    hash_ref['svec'] = 2
    hash_ref['un'] = 2
    hash_ref['vas'] = 2
    hash_ref['veebr'] = 2
    hash_ref['velj'] = 2
    hash_ref['ún'] = 2
    hash_ref['φεβ'] = 2
    hash_ref['ber'] = 3
    hash_ref['brez'] = 3
    hash_ref['kovas'] = 3
    hash_ref['maart'] = 3
    hash_ref['mac'] = 3 
    hash_ref['mar'] = 3
    hash_ref['marc'] = 3
    hash_ref['marco'] = 3
    hash_ref['mars'] = 3
    hash_ref['mart'] = 3
    hash_ref['marts'] = 3
    hash_ref['marz'] = 3
    hash_ref['marzo'] = 3
    hash_ref['março'] = 3
    hash_ref['maw'] = 3
    hash_ref['mrt'] = 3
    hash_ref['márc'] = 3
    hash_ref['märts'] = 3
    hash_ref['märz'] = 3
    hash_ref['ozuj'] = 3
    hash_ref['sak'] = 3
    hash_ref['sus'] = 3
    hash_ref['μάρ'] = 3
    hash_ref['abr'] = 4
    hash_ref['abril'] = 4
    hash_ref['apr'] = 4
    hash_ref['april'] = 4
    hash_ref['avr'] = 4
    hash_ref['avril'] = 4
    hash_ref['bal'] = 4
    hash_ref['dub'] = 4
    hash_ref['ebr'] = 4
    hash_ref['kras'] = 4
    hash_ref['kvit'] = 4
    hash_ref['kwiec'] = 4
    hash_ref['mali traven'] = 4
    hash_ref['nisan'] = 4
    hash_ref['trav'] = 4
    hash_ref['ápr'] = 4
    hash_ref['απρ'] = 4
    hash_ref['geg'] = 5
    hash_ref['kvet'] = 5
    hash_ref['květ'] = 5
    hash_ref['mag'] = 5
    hash_ref['magg'] = 5
    hash_ref['mai'] = 5
    hash_ref['maijs'] = 5
    hash_ref['maio'] = 5
    hash_ref['maios'] = 5
    hash_ref['maj'] = 5
    hash_ref['may'] = 5
    hash_ref['mayis'] = 5
    hash_ref['mayo'] = 5
    hash_ref['mei'] = 5
    hash_ref['máj'] = 5
    hash_ref['svib'] = 5
    hash_ref['trav'] = 5
    hash_ref['veliki traven'] = 5
    hash_ref['μάι'] = 5
    hash_ref['birz'] = 6
    hash_ref['cerv'] = 6
    hash_ref['cher'] = 6
    hash_ref['cherv'] = 6
    hash_ref['czerw'] = 6
    hash_ref['djuni'] = 6
    hash_ref['giugno'] = 6
    hash_ref['haziran'] = 6
    hash_ref['iiun'] = 6
    hash_ref['iiun\''] = 6
    hash_ref['ioun'] = 6
    hash_ref['iun'] = 6
    hash_ref['iuni'] = 6
    hash_ref['iunie'] = 6
    hash_ref['juin'] = 6
    hash_ref['jun'] = 6
    hash_ref['june'] = 6
    hash_ref['junho'] = 6
    hash_ref['juni'] = 6
    hash_ref['junijs'] = 6
    hash_ref['juuni'] = 6
    hash_ref['jún'] = 6
    hash_ref['meh'] = 6
    hash_ref['roz'] = 6
    hash_ref['ιούν'] = 6
    hash_ref['cerven'] = 7
    hash_ref['djuli'] = 7
    hash_ref['gorff'] = 7
    hash_ref['iiul'] = 7
    hash_ref['iiul\''] = 7
    hash_ref['ioul'] = 7
    hash_ref['iul'] = 7
    hash_ref['iuli'] = 7
    hash_ref['iulie'] = 7
    hash_ref['juil'] = 7
    hash_ref['juill'] = 7
    hash_ref['jul'] = 7
    hash_ref['julai'] = 7
    hash_ref['julho'] = 7
    hash_ref['juli'] = 7
    hash_ref['julijs'] = 7
    hash_ref['july'] = 7
    hash_ref['juuli'] = 7
    hash_ref['júl'] = 7
    hash_ref['liepa'] = 7
    hash_ref['lip'] = 7
    hash_ref['lug'] = 7
    hash_ref['lugl'] = 7
    hash_ref['luglio'] = 7
    hash_ref['lyp'] = 7
    hash_ref['mali srpan'] = 7
    hash_ref['srp'] = 7
    hash_ref['temmuz'] = 7
    hash_ref['ιούλ'] = 7
    hash_ref['ag'] = 8
    hash_ref['aout'] = 8
    hash_ref['août'] = 8
    hash_ref['aug'] = 8
    hash_ref['avg'] = 8
    hash_ref['awst'] = 8
    hash_ref['kol'] = 8
    hash_ref['og'] = 8
    hash_ref['rugp'] = 8
    hash_ref['serp'] = 8
    hash_ref['sierp '] = 8
    hash_ref['sierp'] = 8
    hash_ref['srp'] = 8
    hash_ref['veliki srpan'] = 8
    hash_ref['zhniven\''] = 8
    hash_ref['αύγ'] = 8
    hash_ref['eylul'] = 9
    hash_ref['kim'] = 9
    hash_ref['medi'] = 9
    hash_ref['rugs'] = 9
    hash_ref['ruj'] = 9
    hash_ref['sent'] = 9
    hash_ref['sep'] = 9
    hash_ref['sept'] = 9
    # Polish 'set' is too close to English word (and Python type) to use straight
    hash_ref['sett'] = 9
    hash_ref['szept'] = 9
    hash_ref['ver'] = 9
    hash_ref['veras'] = 9
    hash_ref['wrzes'] = 9
    hash_ref['zar'] = 9
    hash_ref['zari'] = 9
    hash_ref['zár'] = 9
    hash_ref['zári'] = 9
    hash_ref['σεπ'] = 9
    hash_ref['ekim'] = 10
    hash_ref['hyd'] = 10
    hash_ref['kastr'] = 10
    hash_ref['oct'] = 10
    hash_ref['okt'] = 10
    hash_ref['ott'] = 10
    hash_ref['out'] = 10
    hash_ref['pazdz'] = 10
    hash_ref['rij'] = 10
    hash_ref['ruj'] = 10
    hash_ref['ríj'] = 10
    hash_ref['spalis'] = 10
    hash_ref['vino'] = 10
    hash_ref['zhovt'] = 10
    hash_ref['οκτ'] = 10
    hash_ref['kasim'] = 11
    hash_ref['lapkr'] = 11
    hash_ref['list'] = 11
    hash_ref['listop'] = 11
    hash_ref['lyst'] = 11
    hash_ref['noem'] = 11
    hash_ref['noia'] = 11
    hash_ref['noiabr'] = 11
    hash_ref['noiabr\''] = 11
    hash_ref['noiem'] = 11
    hash_ref['nop'] = 11
    hash_ref['nov'] = 11
    hash_ref['stud'] = 11
    hash_ref['tach'] = 11
    hash_ref['νοέ'] = 11
    hash_ref['aralik'] = 12
    hash_ref['dec'] = 12
    hash_ref['dek'] = 12
    hash_ref['deke'] = 12
    hash_ref['des'] = 12
    hash_ref['dets'] = 12
    hash_ref['dez'] = 12
    hash_ref['dic'] = 12
    hash_ref['dis'] = 12
    hash_ref['déc'] = 12
    hash_ref['gr'] = 12
    hash_ref['grudz'] = 12
    hash_ref['hrud'] = 12
    hash_ref['pros'] = 12
    hash_ref['rhag'] = 12
    hash_ref['snezh'] = 12
    hash_ref['δεκ'] = 12
    hash_ref['dc'] = 12


def _get_unknown_abbreviations(hash_ref):
    # unknown languages, or nonstandard abbreviations (require period with them))
    hash_ref['Jänn.'] = 1
    hash_ref['Jann.'] = 1
    hash_ref['jänn.'] = 1
    hash_ref['jann.'] = 1
    hash_ref['febr'] = 2
    hash_ref['iiu'] = 6  # Romanian?
    hash_ref['septemb.'] = 9
    hash_ref['agos'] = 8
    hash_ref['octob.'] = 10
    hash_ref['novemb.'] = 11
    hash_ref['noibr'] = 11  # Romanian?
    hash_ref['decemb.'] = 12
    hash_ref['detz'] = 12

# ----------------------------------------------------------------------
# Language-by-language subroutines
# ----------------------------------------------------------------------


def _get_arabic_months(all_months):
    all_months['yanāyir'] = 1
    all_months['yanayir'] = 1
    all_months['yanayir'] = 1
    all_months['fabrayir'] = 2
    all_months['fibrāyir'] = 2
    all_months['fibrayir'] = 2
    all_months['fibrayir'] = 2
    all_months['māris'] = 3
    all_months['maris'] = 3
    all_months['maris'] = 3
    all_months['abrīl'] = 4
    all_months['abril'] = 4
    all_months['ibrīl'] = 4
    all_months['ibril'] = 4
    all_months['abril'] = 4
    all_months['ibril'] = 4
    all_months['māyū'] = 5
    all_months['mayu'] = 5
    all_months['mayu'] = 5
    all_months['yūnyū'] = 6
    all_months['yunyu'] = 6
    all_months['yūnya'] = 6
    all_months['yunya'] = 6
    all_months['yunyu'] = 6
    all_months['yunya'] = 6
    all_months['yuniyu'] = 6
    all_months['yūlyū'] = 7
    all_months['yulyu'] = 7
    all_months['yuliyu'] = 7
    all_months['yūlia'] = 7
    all_months['yulia'] = 7
    all_months['yulyu'] = 7
    all_months['yulia'] = 7
    all_months['aghusṭus'] = 8
    all_months['aghustus'] = 8
    all_months['aġustus'] = 8
    all_months['agustus'] = 8
    all_months['agustus'] = 8
    all_months['sibtambar'] = 9
    all_months['sibtambir'] = 9
    all_months['uktūbar'] = 10
    all_months['uktubar'] = 10
    all_months['uktubir'] = 10
    all_months['nūfambir'] = 11
    all_months['nufambir'] = 11
    all_months['nūfambar'] = 11
    all_months['nufambar'] = 11
    all_months['nufambir'] = 11
    all_months['nufimbir'] = 11
    all_months['dīsambir'] = 12
    all_months['disimbir'] = 12
    all_months['disambir'] = 12
    # Iraq, Syria, Lebanon, Palestine, Jordan months below
    all_months['kānūn ath-thānī'] = 1
    all_months['kanun ath-thani'] = 1
    all_months['shubāṭ'] = 2
    all_months['shubaṭ'] = 2
    all_months['ādhār'] = 3
    all_months['adhar'] = 3
    all_months['naysān '] = 4
    all_months['naysan '] = 4
    all_months['ayyār'] = 5
    all_months['ayyar'] = 5
    all_months['ḥazīrān'] = 6
    all_months['ḥaziran'] = 6
    all_months['tammūz'] = 7
    all_months['tammuz'] = 7
    # all_months['āb'] = 8  # TODO: can we get this to work? like (for instance) "abstract"
    all_months['aylūl'] = 9
    all_months['aylul'] = 9
    all_months['tishrīn al-awwal'] = 10
    all_months['tishrin al-awwal'] = 10
    all_months['tishrīn ath-thānī '] = 11
    all_months['tishrin ath-thani '] = 11
    all_months['kānūn al-awwal'] = 12
    all_months['kanun al-awwal'] = 12


def _get_czech_months(all_months):
    all_months['leden'] = 1
    all_months['ledna'] = 1
    all_months['únor'] = 2
    all_months['unor'] = 2
    all_months['únoru'] = 2
    all_months['unoru'] = 2
    all_months['února'] = 2
    all_months['unora'] = 2
    all_months['březen'] = 3
    all_months['brezen'] = 3
    all_months['března'] = 3
    all_months['brezna'] = 3
    all_months['březnu'] = 3
    all_months['breznu'] = 3
    all_months['duben'] = 4
    all_months['dubna'] = 4
    all_months['květen'] = 5
    all_months['kveten'] = 5
    all_months['květnu'] = 5
    all_months['kvetnu'] = 5
    all_months['května'] = 5
    all_months['kvetna'] = 5
    all_months['červen'] = 6
    all_months['cerven'] = 6
    all_months['červenec'] = 7
    all_months['cervenec'] = 7
    all_months['července'] = 7
    all_months['cervence'] = 7
    all_months['srpen'] = 8
    all_months['srpnu'] = 8
    all_months['září'] = 9
    all_months['zari'] = 9
    all_months['říjen'] = 10
    all_months['rijen'] = 10
    all_months['října'] = 10
    all_months['rijna'] = 10
    all_months['listopad'] = 11
    all_months['listopadu'] = 11
    all_months['prosinec'] = 12
    all_months['prosince'] = 12
    all_months['prosinci'] = 12


def _get_english_months(all_months):
    all_months['january'] = 1
    all_months['february'] = 2
    all_months['march'] = 3
    all_months['april'] = 4
    all_months['may'] = 5
    all_months['june'] = 6
    all_months['july'] = 7
    all_months['august'] = 8
    all_months['september'] = 9
    all_months['october'] = 10
    all_months['november'] = 11
    all_months['december'] = 12


def _get_french_months(all_months):
    all_months['janvier'] = 1
    all_months['février'] = 2
    all_months['fevrier'] = 2
    all_months['mars'] = 3
    all_months['avril'] = 4
    all_months['mai'] = 5
    all_months['juin'] = 6
    all_months['juillet'] = 7
    all_months['août'] = 8
    all_months['aout'] = 8
    all_months['aout'] = 8
    all_months['septembre'] = 9
    all_months['octobre'] = 10
    all_months['novembre'] = 11
    all_months['décembre'] = 12
    all_months['decembre'] = 12


def _get_dutch_months(all_months):
    all_months['januari'] = 1
    all_months['februari'] = 2
    all_months['maart'] = 3
    all_months['april'] = 4
    all_months['mei'] = 5
    all_months['juni'] = 6
    all_months['juli'] = 7
    all_months['augustus'] = 8
    all_months['september'] = 9
    all_months['oktober'] = 10
    all_months['november'] = 11
    all_months['december'] = 12


def _get_finnish_months(all_months):
    all_months['tammikuu'] = 1
    all_months['helmikuu'] = 2
    all_months['maaliskuu'] = 3
    all_months['huhtikuu'] = 4
    all_months['toukokuu'] = 5
    all_months['kesäkuu'] = 6
    all_months['kesakuu'] = 6
    all_months['heinäkuu'] = 7
    all_months['heinakuu'] = 7
    all_months['elokuu'] = 8
    all_months['syyskuu'] = 9
    all_months['lokakuu'] = 10
    all_months['marraskuu'] = 11
    all_months['joulukuu'] = 12


def _get_german_months(all_months):
    all_months['januar'] = 1
    all_months['janaur'] = 1  # common typo
    all_months['februar'] = 2
    all_months['märz'] = 3
    all_months['marz'] = 3
    all_months['mȧrz'] = 3  # this is common, think it's really a typo
    all_months['april'] = 4
    all_months['mai'] = 5
    all_months['juni'] = 6
    all_months['juli'] = 7
    all_months['august'] = 8
    all_months['september'] = 9
    all_months['oktober'] = 10
    all_months['ocktober'] = 10
    all_months['november'] = 11
    all_months['dezember'] = 12


def _get_greek_months(all_months):
    all_months['ianouarios'] = 1
    all_months['ιανουάριος'] = 1
    all_months['fevouarios'] = 2
    all_months['φεβρουάριος'] = 2
    all_months['martios'] = 3
    all_months['μάρτιος'] = 3
    all_months['aprilios'] = 4
    all_months['απρίλιος'] = 4
    all_months['maios'] = 5
    all_months['μάιος'] = 5
    all_months['iounios'] = 6
    all_months['ιούνιος'] = 6
    all_months['ioulios'] = 7
    all_months['ιούλιος'] = 7
    all_months['avgoustos'] = 8
    all_months['αύγουστος'] = 8
    all_months['septemvrios'] = 9
    all_months['σεπτέμβριος'] = 9
    all_months['oktovrios'] = 10
    all_months['οκτώβριος'] = 10
    all_months['noemvrios'] = 11
    all_months['νοέμβριος'] = 11
    all_months['thekemvrios'] = 12
    all_months['δεκέμβριος'] = 12


def _get_hebrew_months(all_months):
    """Hebrew months."""
    # TODO: Add Hebrew alphabet versions? Also look for typos, transliteration variants
    all_months['yanu-ar'] = 1
    all_months['yanuar'] = 1
    all_months['febru-ar'] = 2
    all_months['februar'] = 2
    all_months['mertz'] = 3
    all_months['yuni'] = 6
    all_months['yuli'] = 7
    all_months['ogust'] = 8
    all_months['detzember'] = 12    


def _get_irish_months(all_months):
    all_months['eanáir'] = 1
    all_months['eanair'] = 1
    all_months['feabhra'] = 2
    all_months['márta'] = 3
    all_months['marta'] = 3
    all_months['aibreán'] = 4
    all_months['aibrean'] = 4
    all_months['aíbreán'] = 4
    all_months['aibrean'] = 4
    all_months['bealtaine'] = 5
    all_months['meitheamh'] = 6
    all_months['iúil'] = 7
    all_months['iuil'] = 7
    all_months['lúnasa'] = 8
    all_months['lunasa'] = 8
    all_months['meán fómhair'] = 9
    all_months['mean fomhair'] = 9
    all_months['méan fómhair'] = 9
    all_months['mean fomhair'] = 9
    all_months['deireadh fómhair'] = 10
    all_months['deireadh fomhair'] = 10
    all_months['samhain'] = 11
    all_months['nollaig'] = 12
    all_months['nodlaig'] = 12


def _get_italian_months(all_months):
    all_months['gennaio'] = 1
    all_months['febbraio'] = 2
    all_months['marzo'] = 3
    all_months['aprile'] = 4
    all_months['maggio'] = 5
    all_months['giugno'] = 6
    all_months['guigno'] = 6  # common misspelling
    all_months['luglio'] = 7
    all_months['agosto'] = 8
    all_months['settembre'] = 9
    all_months['ottobre'] = 10
    all_months['novembre'] = 11
    all_months['dicembre'] = 12


def _get_polish_months(all_months):
    all_months['styczeń'] = 1
    all_months['styczen'] = 1
    all_months['luty'] = 2
    all_months['marzec'] = 3
    all_months['kwiecień'] = 4
    all_months['kwiecien'] = 4
    all_months['maj'] = 5
    all_months['czerwiec'] = 6
    all_months['lipiec'] = 7
    all_months['sierpień'] = 8
    all_months['sierpien'] = 8
    all_months['wrzesień'] = 9
    all_months['wrzesien'] = 9
    all_months['październik'] = 10
    all_months['pazdziernik'] = 10
    all_months['listopad'] = 11
    all_months['grudzień'] = 12
    all_months['grudzien'] = 12


def _get_portuguese_months(all_months):
    # TODO: move Galician months to Portuguese? Or separate them out?
    all_months['janeiro'] = 1
    all_months['xaneiro'] = 1  # Old Portuguese?
    all_months['fevereiro'] = 2
    all_months['febreiro'] = 2  # Old Portuguese?
    all_months['março'] = 3
    all_months['marco'] = 3
    all_months['marzo'] = 3  # Old Portuguese?
    all_months['abril'] = 4
    all_months['maio'] = 5
    all_months['junho'] = 6
    all_months['julho'] = 7
    all_months['agosto'] = 8
    all_months['setembro'] = 9
    all_months['outubro'] = 10
    all_months['novembro'] = 11
    all_months['dezembro'] = 12


def _get_romanian_months(all_months):
    all_months['ianuarie'] = 1
    all_months['ianvarie'] = 1
    all_months['ianuar'] = 1
    all_months['februarie'] = 2
    all_months['fevruarie'] = 2
    all_months['martie'] = 3
    all_months['aprilie'] = 4
    all_months['mai'] = 5
    all_months['maiŭ'] = 5
    all_months['maiu'] = 5
    all_months['iunie'] = 6
    all_months['iuniŭ'] = 6
    all_months['iuniu'] = 6
    all_months['iulie'] = 7
    all_months['iuliu'] = 7
    all_months['august'] = 8
    all_months['setiembre'] = 9
    all_months['septembrie'] = 9
    all_months['septemvrie'] = 9
    all_months['octombrie'] = 10
    all_months['octomvrie'] = 10
    all_months['octombre'] = 10
    all_months['noiembrie'] = 11
    all_months['noembre'] = 11
    all_months['noemvrie'] = 11
    all_months['decembrie'] = 12
    all_months['decemvrie'] = 12


def _get_russian_months(all_months):
    all_months['январь'] = 1
    all_months['ianvar\''] = 1
    all_months['janvar\''] = 1
    all_months['февраль'] = 2
    all_months['fevral\''] = 2
    all_months['fevrali'] = 2
    all_months['март'] = 3
    all_months['mart'] = 3
    all_months['mart'] = 3
    all_months['апрель'] = 4
    all_months['aprel\''] = 4
    all_months['май'] = 5
    all_months['mai'] = 5
    all_months['maj'] = 5
    all_months['июньi'] = 6
    all_months['iiun\'i'] = 6
    all_months['jun\''] = 6
    all_months['июльi'] = 7
    all_months['iiul\'i'] = 7
    all_months['jul\''] = 7
    all_months['август'] = 8
    all_months['avgust'] = 8
    all_months['avgust'] = 8
    all_months['сентябрь'] = 9
    all_months['sentiabr\''] = 9
    all_months['sentjabr\''] = 9
    all_months['октябрь'] = 10
    all_months['oktiabr\''] = 10
    all_months['oktjabr\''] = 10
    all_months['ноябрь'] = 11
    all_months['noiabr\''] = 11
    all_months['nojabr\''] = 11
    all_months['декабрь'] = 12
    all_months['dekabr\''] = 12


def _get_spanish_months(all_months):
    all_months['enero'] = 1
    all_months['xaneiro'] = 1  # Galician
    all_months['febrero'] = 2
    all_months['febreiro'] = 2  # Galician
    all_months['marzo'] = 3
    all_months['abril'] = 4
    all_months['mayo'] = 5
    all_months['maio'] = 5  # Galician
    all_months['junio'] = 6
    all_months['xuño'] = 6  # Galician
    all_months['xuno'] = 6  # Galician
    all_months['xuno'] = 6  # Galician
    all_months['julio'] = 7
    all_months['xullo'] = 7  # Galician
    all_months['xulio'] = 7  # Galician
    all_months['agosto'] = 8
    all_months['septiembre'] = 9
    all_months['outubro'] = 10  # Galician
    all_months['octubre'] = 10
    all_months['noviembre'] = 11
    all_months['novembro'] = 11  # Galician
    all_months['diciembre'] = 12
    all_months['decembro'] = 12  # Galician


def _get_thai_months(all_months):
    all_months['makarakhom'] = 1
    all_months['kumphaphan'] = 2
    all_months['minakhom'] = 3
    all_months['mesayon'] = 4
    all_months['pruesaphakho'] = 5
    all_months['mithunayon'] = 6
    all_months['karakadakhom'] = 7
    all_months['singhakhom'] = 8
    all_months['kanyayon'] = 9
    all_months['tulakhom'] = 10
    all_months['pruesajikayon'] = 11
    all_months['thanwakhom'] = 12


def _get_turkish_months(all_months):
    all_months['ocak'] = 1
    all_months['şubat'] = 2
    all_months['subat'] = 2
    all_months['mart'] = 3
    all_months['nisan'] = 4
    all_months['mayis'] = 5
    all_months['haziran'] = 6
    all_months['temmuz'] = 7
    all_months['agustos'] = 8
    all_months['ağustos'] = 8
    all_months['eylül'] = 9
    all_months['eylul'] = 9
    all_months['ekim'] = 10
    all_months['kasim'] = 11
    all_months['aralik'] = 12
    all_months['kanunuevvel'] = 12


def _get_various_months(all_months):
    """
    Varied months.

    It no longer makes sense to add months on a language-by-language basis, as many
    of each languages months will be the same as some other language. So add them here,
    unless we add a language with radically different names.

    This also includes common typos, misspellings, one-offs, and other oddities.
    """

    all_months['jänner'] = 1
    all_months['janner'] = 1
    all_months['februario'] = 2
    all_months['martio'] = 3
    all_months['machi'] = 3
    all_months['avri'] = 4
    all_months['aprili'] = 4
    all_months['iunio'] = 6
    all_months['julius'] = 7
    all_months['juilet'] = 7
    all_months['julli'] = 7
    all_months['aot'] = 8
    all_months['agosti'] = 8
    all_months['agosto'] = 8
    all_months['agustos'] = 8
    all_months['septemba'] = 9  
    all_months['septembri'] = 9
    all_months['septemb'] = 9
    all_months['octob'] = 10
    all_months['oktoba'] = 10
    all_months['novemba'] = 11
    all_months['novembri'] = 11
    all_months['novmbre'] = 11
    all_months['desemba'] = 12
    all_months['disemba'] = 12
    all_months['decembri'] = 12
    all_months['dececember'] = 12
    all_months['decemb'] = 12

    all_months['first month'] = 1
    all_months['second month'] = 2
    all_months['third month'] = 3
    all_months['fourth month'] = 4
    all_months['fifth month'] = 5
    all_months['sixth month'] = 6
    all_months['seventh month'] = 7
    all_months['eighth month'] = 8
    all_months['ninth month'] = 9
    all_months['tenth month'] = 10
    all_months['eleventh month'] = 11
    all_months['twelfth month'] = 12
    all_months['twelvth month'] = 12


def _month_number_returner(month):
    if not month:
        return
    month = month.lower()
    m_ref = get_months_with_abbrevs()
    if month not in m_ref:
        return
    number = m_ref[month]
    if number:
        return number


def _season_number_returner(season):
    if not season:
        return
    season = season.lower()
    seasons = {}
    _get_seasons(seasons)
    if season in seasons:
        return seasons[season]
