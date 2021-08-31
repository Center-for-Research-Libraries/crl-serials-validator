"""
Functions taken from the Normalizer for separating index & supplement from regular holdings.
"""

import re
import sys
from collections import OrderedDict
# from pprint import pprint


def remove_supplements_from_holdings(holdings):
    """
    Remove supplement string from holdings.
    """
    working_holdings = re.sub("supp?ressed", "", holdings, flags=re.I)
    # semicolons in parens will break some supplement regexs
    working_holdings = re.sub(r"(\([^)]*);([^)]*\))", "\\1,\\2", working_holdings)

    # "hors-série" or "hors series" means "special issue" and in practice is always a supplement
    working_holdings = re.sub(r"hors[-\s]*series?", "supp", working_holdings, flags=re.I)

    if "supp" in working_holdings.lower():
        start_terms = ["supp", "special suppl", "*supp", "stastical supp", "[suppl"]
        for start_term in start_terms:
            if working_holdings.lower().startswith(start_term):
                # entire statement is supplements
                return "", holdings, True
    # else:
    #     supps = []
    #     m = re.findall("( *(?:&|and) *(suppl(?:ement)?s?\.?[^\(,;]*))", holdings)
    #     for segment in m:
    #         supps.append(segment[1])
    #         holdings = holdings.replace(segment[0], "")

    #     return holdings, supps.join("; "), False

    # deal with something like "2015  no. 4-6 + suppl. (no. 298-300)"
    # normally we expect a year for the overall volume in the ending parens ("v.14 + suppl. 8 (2011)"), so this is a
    # special case we're looking for
    m = re.search(r"(:? *(?:\+|&|and) *(?:annual *|cum(?:ulative)?\.? *|special *)?suppl?s?\.?[^()]*\([^)]+\))", 
                  working_holdings, flags=re.I)
    if m:
        capture_text = m.group(1)
        if not re.search(r"\([^)]*(?:19\d\d|20[0-2]\d)", capture_text):
            working_holdings = working_holdings.replace(capture_text, "")
            capture_text = re.sub(r"^[:;]* *(?:&|\+|and) *", "", capture_text)
            return working_holdings, capture_text, True

    # regexs by category -- to remove, show the entire string is a supplement, or to extract the supplement segment(s)
    suppl_regexs = OrderedDict({
        # "v. 1, no. 1-4 (Apr/May-Nov/Dec 1988) includes suppl. to Sept/Oct 1988"
        "incl[^;]*supp[;]*": "capture",
        # "v. 1 & suppl."
        r":? *(?:\+|&|and) *(?:annual *|cum(?:ulative)?\.? *|special *)?suppl?s?\.?[^\(\)]*": "capture",
        # "1998/99-2008 & 2008 Supplement"
        r" *(?:&|and)[^;]*supp[^;\(,]*": "capture",
        # "1998/99-2008; 2008 Supplement"
        "[;][^,;]+supp[^;]+": "capture",
        # "v.1 suppl." or "(1972) suppl"
        "^ *[^,;]+supp": "entire",
        # v.23;supl.
        "; *suppl": "capture",
        # "v.1, suppl", "v.1, pt.3, suppl." and many variants
        r"^ *[a-z]+\.? *\d+(?:[/-]\d+)?(?:[ :,]*[a-z]+\.? *\d+(?:[/-]\d+)?)? *?,? *\(?supp": "entire",
        # "2001, suppl."
        r"^ *\d+(?:[/-]\d+)?,? *supp": "entire",
        # "19.Bd., suppl. (1906)" and many variants
        r"^ *[\d\w\.\s]+, (?:annual *|cum(?:ulative)?\.? *|special *)?supp": "entire",
        # Jahrg. 16 (1907), suppl.
        r"(?<=\)),[^\(,;]*supp[^,;]*": "entire",
        # 2005-2010, 2005 Suppl.
        r"[,;] *((?:1[6789]\d\d|20[012]\d) *suppl?(?:ement)?\.? *$)": "capture",
        # "& special issue"
        r"(?:&|\+|and) *(spec(?:ial)?\.? *(?:iss(?:ue)?\.?|no\.|num(?:ber)?\.?)[^\(]*)": "capture",
        # "special issue" or "special number" without preceding semicolon, etc break
        r"^[^;,]*spec(?:ial)?\.? *(?:iss(?:ue)?\.?|no\.|num(?:ber)?\.?).*": "entire",
        # "vol. 28, special issue no. 1 (June 2012)"
        r"(?:v(?:ol)?|no)\.? *\d+(?:/\d+)? *, *special iss.*": "entire",
        # "v. 14 (2010), special issue 2010, Discussion forum 5 (2010)"
        r", *(spec(?:ial)?\.? *(?:iss(?:ue)?\.?|no\.|num(?:ber)?\.?).*)": "capture",
        # '1901, with supp. 1901/11'
        r"[;,]? *(?:with|w\.?/?) *(supp.*)": "capture",
        # 1959/60-1975/76; 1975/76, suppl.
        "; *([^;]*supp[^;]*)": "capture",
    })
    for r in suppl_regexs:
        m = re.findall(r, working_holdings, flags=re.I)
        if not m:
            continue
        if suppl_regexs[r] == "entire":
            return "", holdings, True
        for i in range(0, len(m)):
            working_holdings = working_holdings.replace(m[i], "")
            if suppl_regexs[r] == "capture":
                m[i] = re.sub(r"^[:;]* *(?:&|\+|and) *", "", m[i])
        if suppl_regexs[r] == "capture":
            suppls = "; ".join(m)
            return working_holdings, suppls, True
        else:
            return working_holdings, "", True

    if "supp" in holdings.lower() and "suppress" not in holdings.lower():
        # haven't found the supplement! err on the side of calling the whole thing a supplement
        return "", holdings, True
    return holdings, "", False


def remove_indexes_from_holdings(holdings):
    """
    Remove indexes from holdings string and return them.
    """
    if "ind" not in holdings.lower():
        if "author" in holdings.lower():
            # something like "v. 21, Subject Author (A-F) 1990" that's actually an index
            holdings = re.sub("(authors?(?:/[a-z]+)?)", "\\1 index", holdings, flags=re.I)
        else:
            return holdings, "", False
    if not re.search(r"ind(?:ex|xe|ic[ei]|eks|ec|\.)", holdings, flags=re.I):
        if not re.search(r"(?:subj(?:ect)?|cum(?:ulative)?|auth(?:or)?|master)[\. ]*ind", holdings):
            if not re.search(r"^[a-z\. ]+ind", holdings, flags=re.I):
                return holdings, "", False

    original_holdings = holdings
    holdings = volume_transform(holdings)

    # normalize index word
    holdings = re.sub("ind(?:ex|xe|ic[ei]|eks|ec)", "index", holdings, flags=re.I)
    holdings = holdings.replace("index.", "index ")

    # "http://www.ethnomusic.ucla.edu/pre/index.html"
    holdings = re.sub(r"index\.(?:html?|php)", "", holdings, flags=re.I)

    # "index" appears before any digits -- take whole string as index
    if re.search(r"^\D*index", holdings, flags=re.I):
        return "", holdings, True
    # UNREACHABLE SO REMOVED
    # return "", holdings, True
    # v. 15-16 (1969-1973) & Index vo. 1-10
    # no. 797-800 (May 1999-Sept. 1999) & 1999 index
    # v.39:1991+index
    m = re.search(r"( *(?:and|&|\+|incl\.?) *([^;,]*index[^;,]*))", holdings, flags=re.I)
    if m:
        replacement_string = m.group(1)
        y = re.search(r"[^(]+(\([^)]*(?:1[6789]\d\d|20[012]\d)?[^)]*\) *$)", replacement_string)
        if y:
            replacement_string = replacement_string.replace(y.group(1), "")
        index_string = m.group(2)
        holdings = holdings.replace(replacement_string, "")
        return holdings, index_string, True

    # v. 1-7 (1907-1913:Index)
    if ';' not in holdings and re.search(":[^,]*index", holdings, flags=re.I):
        return "", holdings, True

    # Vol. 1-v. 29; index, v.1-30 -- index after a semicolon, take all until next semicolon
    m = re.search("(; *([^;]*index[^;]*))", holdings, flags=re.I)
    if m:
        replacement_string = m.group(1)
        index_string = m.group(2)
        holdings = holdings.replace(replacement_string, "")
        return holdings, index_string, True

    # Index 1992
    # Subject index 1978
    if re.search(r"^[a-z\. ]+ind", holdings, flags=re.I):
        return "", original_holdings, True

    # v. 19 (1972)  INDEX 18-19 <-- note double spaces
    m = re.search(r"\)(  +(index[^;,]*))", holdings, flags=re.I)
    if m:
        replacement_string = m.group(1)
        index_string = m.group(2)
        holdings = holdings.replace(replacement_string, "")
        return holdings, index_string, True

    # v. 8, Index Sect. 3-4 (1970)
    if re.search(r"^ *v(?:ol)?\.? *\d\d?\d?[,:][a-z_\s\.]*index", holdings, flags=re.I):
        return "", original_holdings, True

    # 2008: index
    # 2008, index
    if re.search(r"^\d\d\d\d(?: *[/-] *\d\d(?:\d\d)?)? *[:,\[(] *ind", holdings, flags=re.I):
        return "", original_holdings, True

    # any time the word "index" appears before a comma or semicolon appears in the string
    if re.search(r"^[^;,]*index", holdings, flags=re.I):
        return "", original_holdings, True

    # v.1-10 index
    if re.search(r"^ *v\. *\w+( *[/-] *\w+), *ind", holdings, flags=re.I):
        return "", original_holdings, True

    # no. 363-373 (2000), Cum. index: no. 1-363 (1964-2000)
    # v.9-240; Subject index, v.1-170; Name index, v.1-58
    pre_index_words = r"(?:subj?(?:ect)?|name|auth(?:or)?|cum(?:ulative)?)?\.?"
    m = re.search("([;, ]+{} *index:?.*)".format(pre_index_words), holdings, flags=re.I)
    if m:
        index_string = m.group(1)
        holdings = holdings.replace(index_string, "")
        index_string = re.sub("^[ ,;]*", "", index_string)
        return holdings, index_string, True

    m = re.findall(r" *(?:and|&|\+)[a-z\. ]*index?[^(-]*", holdings, flags=re.I)
    if m:
        for index_segment in m:
            holdings = holdings.replace(index_segment, "")
            holdings = holdings.replace('()', "")
        return holdings.strip(), "; ".join(m), True

    return original_holdings, "", True


def volume_transform(holdings_segment):
    """
    Try to transform words that will ultimately end up as "v."
    """
    original_string = holdings_segment
    vol_words = get_vol_words()
    ordinals_regex = get_regex("ordinals")
    years_regex = get_regex("years")

    # in something like "r. 1: v. 26-31 (1915-1921)" the "r." doesn't seem to function as a series
    # usually this seems to be recorded like "v.26-31...", so drop the "r. 1"
    # don't fully understand this form of enumeration, so maybe revisit this decision
    holdings_segment = re.sub(r"(\b)r\. *\d+ *: *v\.", "\\1 v.", holdings_segment)

    # other strings starting with "r." we'll treat it as a volume
    # note that they may contain non-English volume words (as in "r.60:z.237/238-239/240 (2011)")
    # we'll deal with those at the end of the function
    holdings_segment = re.sub(r"^ *[Rr]\. *(\d+)", "v.\\1", holdings_segment)

    # capital to capital that might be mistaken later for a roman numeral
    non_roman = "[ABDEFGHJKNOPQRSTUVWYZ]"
    holdings_segment = re.sub(r"(\b)[A-Z] *- *{}(\b)".format(non_roman), "\\1 \\2", holdings_segment)
    holdings_segment = re.sub(r"(\b){} *- *[A-Z](\b)".format(non_roman), "\\1 \\2", holdings_segment)

    # "nol." appears as typo for both "vol." and "no."
    if 'nol.' in holdings_segment:
        if 'no.' in holdings_segment:
            holdings_segment = holdings_segment.replace("nol.", "v.")
        elif 'v.' in holdings_segment:
            holdings_segment = holdings_segment.replace("nol.", "no.")
    # "(año 1988)" should be "(1988)", not "(v.1988)"
    holdings_segment = re.sub(r"(\([^(]*)ann?o ({})".format(years_regex), "\\1 \\2", holdings_segment, flags=re.I)
    # vyps.
    if re.search(r"\bTomo|\bTom|\btom|\bt\.|\bT\.", original_string):
        holdings_segment = re.sub(r"[Vv]yp\.?\s*", "no.", holdings_segment)
    else:
        holdings_segment = re.sub(r"[Vv]yp\.?\s*", "v.", holdings_segment)

    holdings_segment = re.sub(r"(\d+)\.? *jaarg(?:ang)?", "v.\\1", holdings_segment)

    # "ann. 6" of "81.-84. ann.)"
    holdings_segment = re.sub(r"(\b)ann(\b)", "\\1v.\\2", holdings_segment, flags=re.I)

    # "21st:v.2 (1986)"
    holdings_segment = re.sub(r"(\b)(\d+){}:? *v\. *(\d\d?\d?)(\b)".format(ordinals_regex), "\\1v.\\2 no.\\3\\4",
                              holdings_segment, flags=re.I)

    # "jahrg" can turn other indicators from vol to num
    if "jahrg" in holdings_segment.lower():
        # eliminate "jahrg" when it's only referring to a year
        if re.search(r"jahrg\.? *(?:1[6-9]\d\d|20[01]\d)", holdings_segment, flags=re.I):
            holdings_segment = re.sub(r"jahrg\.? *", "", holdings_segment, flags=re.I)
        else:
            if re.search(r"\b(?:t|bd)\.? *\d", holdings_segment, flags=re.I):

                holdings_segment = re.sub(r"(\b)(?:t|bd)\.? *(\d)", "\\1no.\\2", holdings_segment, flags=re.I)
            # 3. Jahrg., 1. T. (1925)
            holdings_segment = re.sub(r", (\d\d?\d?)\.? (?:t|bd)\.?", ", no.\\1", holdings_segment, flags=re.I)

    # TODO: "Teil/Teilband"/"T" can indicate a series, volume, or number.
    # "v. 10 Teil 1-3" -- teil as "no."
    holdings_segment = re.sub(r"(\b)v\. *(\d\d?\d?)[,:\s]*t(?:eil)?\.? *(\d\d?\d?(?: *[/-] *\d\d?\d?)?)",
                              "\\1v.\\2:no.\\3", holdings_segment, flags=re.I)

    # "Vol. 2 (1946)-t. 33 (1991)"
    if re.search(r"\b(?:v\.|vol)", holdings_segment, flags=re.I):
        holdings_segment = re.sub(r"- *(?:t\.|teil)", "-v.", holdings_segment, flags=re.I)

    # "v. 39, pt. 2, T. 2 (2009)" -- remove "t." and number when it comes after a volume
    holdings_segment = re.sub(r"(\bv(?:ol)?\. *\d.*\b)t(?:ome|eil|eilband)?\.? *\d+,?", "\\1 ", holdings_segment,
                              flags=re.I)

    # "t.131:livr.1548-1553" -> "livre" to indicate number
    holdings_segment = re.sub("teil", "T.", holdings_segment, flags=re.I)
    if re.search(r"\b[Tt]\.? *\d", holdings_segment) and re.search(r"\blivr?e?\.? *\d", holdings_segment):
        holdings_segment = re.sub(r"(\b)livr?e?\.? *", "\\1no.", holdings_segment)
    # "t.86:kn.1:1993" -> "kn."/"knj."/"kniga" to represent number
    if re.search(r"\b[TtGg]\.? *\d", holdings_segment) and re.search(r"\bknj?(?:iga)?\.? *\d", holdings_segment):
        holdings_segment = re.sub(r"(\b)knj?(?:iga)?\.? *", "\\1no.", holdings_segment)

    # TODO: "Teil"/"Teilband"/"T" seems to have a complex relationship with "Band/Bd"

    # "s" for "seit"
    holdings_segment = re.sub(r"^ *[Ss]\.? *(\d)", "v.\\1", holdings_segment)

    # 54e annee
    holdings_segment = re.sub("1re ann[ée]e", "v.1", holdings_segment, flags=re.I)
    holdings_segment = re.sub(r"(\d+)[e\.]+ ann[ée]e", "v.\\1", holdings_segment, flags=re.I)

    # "annee23" is a relatively common sort of error
    holdings_segment = re.sub(r"ann[ée]e(\d)", "annee \\1", holdings_segment, flags=re.I)

    holdings_segment = re.sub(r"anno(\d)", "annee \\1", holdings_segment, flags=re.I)

    # to deal with things like "Jahrg23"
    for volume_word in vol_words:
        holdings_segment = re.sub(r"(\b){}(\d)".format(volume_word), "\\1v.\\2", holdings_segment, flags=re.I)

    vol_regex = r'(\b)' + r'\.?(\b)|(\b)'.join(vol_words) + r'\.?(\b)'
    holdings_segment = re.sub(vol_regex, "\\1v.\\2", holdings_segment, flags=re.I)

    # ed. 24
    holdings_segment = re.sub(r"(\b)[Ee]d\.? *(\d{1,3}(\b))", "\\1v.\\2\\3", holdings_segment)

    # "14th ed."
    holdings_segment = re.sub(r"(\d+) *(?:st|nd|rd|th|er|re|e)\.? ed(?:ition)?\.* *", "v.\\1 ", holdings_segment)

    # "4th year (1998)"
    holdings_segment = re.sub(r"(\d+){} y(?:ea)?r\.?".format(ordinals_regex), "v.\\1", holdings_segment, flags=re.I)

    # something like "year 1" without pulling in "year 1973"
    holdings_segment = re.sub(r"year (\d{1,3})(\b)", "v.\\1\\2", holdings_segment, flags=re.I)

    if not re.search(r"v\.* *\d", holdings_segment):
        # "r.64"
        holdings_segment = re.sub(r"(\b)r\. *(\d{1,3})", "\\1v.\\2", holdings_segment)

    # TODO: Is this OK? Should the if be commented out and the my_regex exposed?
    # if "year" in holdings_segment and "v." not in holdings_segment:
        holdings_segment = re.sub(r"(\d+) year", "v.\\1", holdings_segment)

    holdings_segment = re.sub(r"(\b)d\. *(\d)", "\\1v.\\2", holdings_segment)

    holdings_segment = re.sub(r"v\.ol\s*", "v.", holdings_segment)
    holdings_segment = re.sub(r"v\.e\s*", "v.", holdings_segment)
    holdings_segment = holdings_segment.replace("v. ", "v.")
    holdings_segment = re.sub(r"v\.\.+", "v.", holdings_segment)
    holdings_segment = re.sub(r"v\.(\d+), no\.? *(\d)", "v.\\1 no.\\2", holdings_segment)

    # "section" or an abbreviation used as number
    if 'no.' not in holdings_segment and 'sec' in holdings_segment.lower():
        holdings_segment = re.sub(r"sect?(?:ion)?\.? *(\d{1,3}\b)", r"no.\1", holdings_segment, flags=re.I)

    # something like "17. Jahr (2004)" will be "17. v. (2004)" and will wind up as "v.17-v.2004"
    holdings_segment = re.sub(r"(\b)(\d{1,3})\.? *v\. *\(", "\\1v.\\2 (", holdings_segment)
    if 'v.' not in holdings_segment and re.search(r"\(\d\d?\d?(?:st|nd|rd|th|e|me)", holdings_segment):
        holdings_segment = re.sub(r"\((\d\d?\d?)(?:st|nd|rd|th|e|me)\.? *", "(v.\\1", holdings_segment)

    # "203. Bd. (Jahrg. 1994)-206. Bd. (Jahrg. 1997)" now will be "v.203 (v. 1994)-v.206 (v. 1997)"

    holdings_segment = re.sub(r"(\b)v\. *(\d{1,3}) *\( *v\. *(\d\d\d\d)(\b)", "\\1v.\\2 (\\3\\4", holdings_segment)

    # TODO: The below is mainly for the ReCap project. Keep it after that?
    # "v.A77 (2003:June-Dec.)" to "v.77 (2003:June-Dec)"
    holdings_segment = re.sub(r"(\b)v\. *[A-Z](\d)", "\\1v.\\2", holdings_segment)

    # keep separate volumes and years in something without parens like "v. 1767-1772  1943-44"
    holdings_segment = re.sub(r"(\b)v\. *(\d\d\d\d(?: *- *(?:v\.)? *\d\d\d\d)?) *(\d\d\d\d(?: *[/-] *\d\d\d?\d?)?)(\b)",
                              "\\1v.\\2 (\\3)\\4", holdings_segment)

    # something like "v. 1992" to "1992"
    if not re.search(r"\([^)]*(?:1[6-9]\d\d|20[01]\d)", holdings_segment):
        holdings_segment = re.sub(r"(\b)v\. *((?:1[6-9]\d\d|20[01]\d))", "\\1\\2", holdings_segment)

    # something like "ano:40 (2003)" will now be "v.:40 (2003)"
    holdings_segment = re.sub(r"(\bv\.): *(\d)", "\\1\\2", holdings_segment)

    # "c.1" can occasionally mean "v.1" instead of copy 1.
    # TODO: improve dealing with "c." as volume
    if 'c.' in holdings_segment.lower():
        if not re.search(r"\bv\.\d", holdings_segment):
            if re.search(r"\bc\.\d+:no", holdings_segment, flags=re.I):
                holdings_segment = re.sub(r"(\b)[Cc]\. *", "\\1v.", holdings_segment)
            # assume any "c." followed by double digits won't be a copy number
            elif re.search(r"\bc\. *\d\d", holdings_segment, flags=re.I):
                holdings_segment = re.sub(r"(\b)[Cc]\. *", "\\1v.", holdings_segment)
    # at this point, "Jahrg.10:v.1 (1989)" will be "v.10:v.1 (1989)"
    holdings_segment = re.sub(r"(\b)v\. *(\d+) *: *v\. *(\d+)(\b)", "\\1v.\\2:no.\\3\\4", holdings_segment)

    # 1. Jahrg. (März 1951)-40. Jahrg., 126 Heft. (Dez. 1990)
    holdings_segment = re.sub(r"-(\d+)\. *v\.", "-v.\\1", holdings_segment)

    # "2000-2002 (15.-17. Jahrg.)", which will now be "2000-2002 (15.-v.17)"
    holdings_segment = re.sub(r"\((\d{1,3})\. *- *v\.", "(v.\\1-v.", holdings_segment)

    # volumes with letters -- "v. 1D, n. 1 (Jan/Feb 1982)-v. 20D, n. 12 (1998)"
    holdings_segment = re.sub(r"(\b)v\. ?(\d{1,3})[A-Z](\b)", "\\1v.\\2\\3", holdings_segment)

    # "15th, v.1-2 (1911)" and the like
    if re.search(r"^ *\d+{}[\s,]+v\. *\d".format(ordinals_regex), holdings_segment):
        m = re.findall(r"(\b\d+{}[\s,]*v\. *\d+(?: *- *(?:v\. *)?\d+)?)".format(ordinals_regex), holdings_segment, 
                       flags=re.I)
        for segment in m:
            updated_segment = segment.replace("v.", "no.")
            updated_segment = re.sub(r"(\d+){}".format(ordinals_regex), "v.\\1", updated_segment, flags=re.I)
            holdings_segment = holdings_segment.replace(segment, updated_segment)

    # for some reason "no.58-60 (v.30-31, 2010-2011)" won't normalize correctly with the comma in the parens
    holdings_segment = re.sub(r"\((v\.\d+ *- *\d+), *({})".format(years_regex), r"\(\1 \2", holdings_segment)

    # leave with normalized spacing
    holdings_segment = re.sub(r"(\b)v\. *(\d)", "\\1v.\\2", holdings_segment)

    # TODO: something like "anno 6 (v.1-2)" will here leave us with "v.6 (v.1-2)

    return holdings_segment


def get_vol_words():
    """
    A list of words that can generally be normalized to "v."
    Note that these are the my_regex versions of the words.
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
        "j",
        "jahrbuch",
        "ja[ah]rg?(?:ang)?",
        "jild",
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
        "sal(?:-i)?"
        "(?:al-)?sanah",
        "sefer",
        "sene",
        "sb",
        "sbornik",
        "sv[ae]zek",
        "t",
        r"tah(?:un|\.)?",
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
    return vol_words


def get_regex(wanted_regex):
    if wanted_regex == "years":
        return _get_years_regex()
    elif wanted_regex == "slash_year":
        return _get_year_slash_regex()
    elif wanted_regex == "year_range":
        return _get_year_range_regex()
    elif wanted_regex == "possible_year":
        return _get_possible_year_regex()

    regexes = {
        "ordinals": "(?:st|nd|rd|th|er|re|e(?:me)?)",
        "months": "(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)",
        "islamic_years": r'1[234]\d\d(?:-(?:1[234])?\d\d)?',
        "convertible_islamic_years": r'1(?:3[4-9]\d|4[0-4]\d)'
    }

    try:
        return regexes[wanted_regex]
    except IndexError:
        sys.exit("Wanted my_regex not found. my_regex is {}.".format(wanted_regex))


def _get_years_regex():
    years_regex = r"(?:1[6789]\d\d|20[01]\d)"
    return years_regex


def _get_year_slash_regex():
    year_regex = _get_years_regex()
    year_slash = r"{0}(?:/{0})?".format(year_regex)
    return year_slash


def _get_year_range_regex():
    year_slash_regex = _get_year_slash_regex()
    year_range_regex = r"{0}(?:-{0})?".format(year_slash_regex)
    return year_range_regex


def _get_possible_year_regex():
    year_range_regex = _get_year_range_regex()
    possible_year_regex = r"(?: \({}\))?".format(year_range_regex)
    return possible_year_regex
