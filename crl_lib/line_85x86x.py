"""
Library to read and convert 85x/86x lines in MARC into text holdings strings.

Converter creates two main lists. output_strings is a list of three lists of holdings strings, the three lists being regular holdings, indexes, and supplements.


Typical usage:

    from line85x86x import Convert85x86x

    converter = Convert85x86x(marc_record)
    output_strings_with_notes = converter.output_strings_with_notes
    output_strings = converter.output_strings


"""

import re
from collections import OrderedDict, namedtuple


class RulesFor85x86x:
    """
    Dicts & sets of legal values for 85x/86x fields.

    This should probably just be a dict or a set of dicts and lists, but instead I'm using it as 
    a base class for the Read85x86xChecks just because it's then slightly more straightforward to
    access the values in this class in the child class. They could also just all go into the 
    child class, but I think it's easier to read if they're kept separate.

    Set loose_rules to False to force warning messages on every incorrect entry. Setting loose_rules
    to True allows the following:

        * Any combination of letters, dash, or slash are OK instead of digits in a month or seasons
          field. So "Spring/Summer" will be OK instead of "23/34".
        * Allows seasons 13, 14, 15, and 16 for Spr through Win
        * Allows seasons in months subfields (i.e., a "month" of 23 will return "Fall")
        * Allows months in seasons subfields (i.e., "21-11" returns "Spring-Nov")
        * adds $i (year) and $j (month) to 853s that don't have one or both fields
        * label "(no.)" always gets converted to "no."
        * obvious years in a 863/864/865 $j are treated as years, if there is no $i

    """

    fields_86x_to_85x = {'863': '853', '864': '854', '865': '855'}
    fields_85x = {'853', '854', '855'}
    fields_86x = {'863', '864', '865'}
    
    seasons = {
        "21": "Spr",
        "22": "Sum",
        "23": "Fall",
        "24": "Win"
    }

    # common but incorrect values for seasons
    loose_seasons = {
        "13": "Spr",
        "14": "Sum",
        "15": "Fall",
        "16": "Win"
    }

    months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    caption_subfield_types = [
        "enumeration", "secondary_enumeration", "chronology"]

    caption_subfields = {
        "enumeration": ['a', 'b', 'c', 'd', 'e', 'f'],
        "secondary_enumeration": ['g', 'h'],
        "chronology": ['i', 'j', 'k', 'l', 'm']
    }

    all_caption_subfields = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'}

    delimiters = {
        "853": {
            1: {'0', '1', '2', '3'},
            2: {'0', '1', '2', '3'}
        },
        "854": {
            1: {'0', '1', '2', '3'},
            2: {'0', '1', '2', '3'}
        },
        "855": {
            1: {'/', '\\', '# '},
            2: {'/', '\\', '# '},
        },
        "863": {
            1: {'/', '\\', '#', '3', '4', '5'},
            2: {'/', '\\', '#', '0', '1', '2', '3', '4'},
        },
        "864": {
            1: {'/', '\\', '#', '3', '4', '5'},
            2: {'/', '\\', '#', '0', '1', '2', '3', '4'},
        },
        "865": {
            1: {'/', '\\', '#', '4', '5'},
            2: {'/', '\\', '#', '1', '3'},
        },
    }

    subfields_85x = [
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',  # enumeration caption
        'i', 'j', 'k', 'l', 'm',                 # chronology caption
        'n', 'p', 'u', 'v', 'w', 'x', 'y', 'z',  # publication pattern
        'o', 't',                                # other captions
        '2', '3', '6', '8'                       # control subfields
    ]
    subfields_86x = [
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',  # enumeration
        'i', 'j', 'k', 'l', 'm',                 # chronology
        'n', 'o', 'p', 'q',                      # descriptors
        's', 't', 'w',                           # numbers and codes
        'x', 'z',                                # notes
        '6', '8'                                 # control subfields
    ]

    def __init__(self, loose_rules=True):
        """        
        Setting loose_rules to True allows several "non-canonical" things to pass through the process.
        Set to False for strict error checking.
        See the top note for details.
        """
        self.loose_rules = loose_rules

        # TODO: Beleive the below is no longer used anywhere:
        # self.lines = {
        #     "853": [],
        #     "854": [],
        #     "855": [],
        #     "863": [],
        #     "864": [],
        #     "865": [],
        # }


class Read85x86xChecks(RulesFor85x86x):
    """
    A series of validity checks for 85x/86x fields
    """

    def __init__(self):
        super().__init__()
        self.warnings = []
        self.errors = []
        self.current_identifier = ""

    def add_warning_message(self, warning_message):
        if self.current_identifier:
            warning_message = f"{self.current_identifier}: " + warning_message
        self.warnings.append(warning_message)

    def check_delimiters(self, delimiters, field):
        counts = ["", "1st", "2nd"]
        for i in range(1, 3):
            if delimiters[i] not in self.delimiters[field][i]:
                warning_message = 'Illegal {} delimiter "{}" in field {}'.format(
                    counts[i], delimiters[i], field)
                self.add_warning_message(warning_message)

    def check_subfield(self, subfield_label, subfield, subfields_dict, field):
        self.check_subfield_exists(subfield_label, subfield, field)
        self.check_subfield_duplicated(
            subfield_label, subfield, subfields_dict, field)
        self.check_legal_subfield(subfield_label, field)

    def check_legal_subfield(self, subfield_label, field):
        warning_needed = False
        if field.startswith('85'):
            if subfield_label not in self.subfields_85x:
                warning_needed = True
        elif subfield_label not in self.subfields_86x:
            if subfield_label != 'v' or field != '865':
                warning_needed = True
        if warning_needed:
            warning_message = f'Illegal subfield "{subfield_label}" in field {field}'
            self.add_warning_message(warning_message)

    def check_subfield_exists(self, subfield_label, subfield, field):
        if not subfield:
            warning_message = f"Blank subfield {subfield_label} in field {field}"
            self.add_warning_message(warning_message)

    def check_subfield_duplicated(self, subfield_label, subfield, subfields_dict, field):
        if subfield_label in subfields_dict and subfield_label in self.all_caption_subfields:
            warning_message = f"Duplicated subfield {subfield_label} in field {field}"
            self.add_warning_message(warning_message)

    def check_85x_line(self, field_dict):
        if '8' not in field_dict['subfields']:
            field_dict['subfields']['8'] = "9999"
            warning_message = "Missing $8 in field {}".format(field_dict["field"])
            self.add_warning_message(warning_message)
        if self.loose_rules is True:
            # add i (year) and j (month/season) fields if they don't exist, as these are sometimes excluded by accident
            if "i" not in field_dict["subfields"]:
                field_dict["subfields"]["i"] = "(year)"
            if "j" not in field_dict["subfields"]:
                field_dict["subfields"]["j"] = "(month)"

    def check_86x_line(self, field_dict):
        if '8' not in field_dict['subfields']:
            field_dict['subfields']['8'] = "9999.1"
            warning_message = "Missing $8 in field {}".format(field_dict["field"])
            self.add_warning_message(warning_message)
        else:
            field_dict['subfields']['8'] = self.check_86x_subfield_8(field_dict['subfields']['8'])
        if self.loose_rules is True:
            if "i" not in field_dict["subfields"] and "j" in field_dict["subfields"]:
                # treat year in $j with no $i as a $i
                if re.search("(?:1[789]\d\d|20[012]\d)", field_dict["subfields"]["j"]):
                    field_dict["subfields"]["i"] = field_dict["subfields"]["j"]
                    del(field_dict["subfields"]["j"])

    def check_86x_subfield_8(self, subfield_8):
        """
        Look for & try to correct errors in $8. Right now only looking for lack of commas, as in:
            =863  40$816$a23-27$b6-5/6$i1928-1932
        Convert that to "$81.6"
        """
        if '.' not in subfield_8:
            fixed_subfield_8 =  f"{subfield_8[:1]}.{subfield_8[1:]}"
            warning_message = f"Probable illegal $8: {subfield_8}"
            self.add_warning_message(warning_message)
            return fixed_subfield_8
        else:
            return subfield_8

    def check_for_too_many_dashes_in_enumeration_or_chronology(self, segments, raw_data):
        """Look for a holdings segment like "1-3-4"."""
        if len(segments) == 2 and '-' in segments[1]:
            warning_str = f"Too many dashes in holdings string {raw_data}"
            self.warnings.append(warning_str)


class Read85x86x(Read85x86xChecks):
    """
    Class to read 85x/86x lines from MARC.
    """

    def __init__(self, input_str):
        super().__init__()

        self.holdings_lines = []
        input_str = re.sub("\r", "", input_str)
        self.input_list = input_str.split("\n")
        self.convert_input_to_readable_lines()

    def convert_input_to_readable_lines(self):
        for i in range(0, len(self.input_list)):
            m = re.search(r"^[=\s]*((?:\d\d\d|LDR))\s*([^\n]+)", self.input_list[i])
            try:
                field = m.group(1)
            except AttributeError:
                continue
            # only keep relevant fields
            if field not in self.fields_85x and field not in self.fields_86x:
                continue
            self.read_line(self.input_list[i])

    def read_line(self, line):
        line = line.strip()
        line = re.sub(r"\t", "  ", line)
        m = re.search(r"^[=\s]*((?:LDR|\d\d\d))\s+([0-9/\\#]) *([0-9/\\#]) *(.+)", line)
        try:
            delimiters = {}
            field, delimiters[1], delimiters[2], subfields_data = m.groups()
        except AttributeError:
            return    
        if field in self.fields_85x or field in self.fields_86x:
            self.check_delimiters(delimiters, field)
        subfields_dict = self.read_subfields(subfields_data, field)

        self.holdings_lines.append(
            {
                "field": field,
                "delimiter_1": delimiters[1],
                "delimiter_2": delimiters[2],
                "subfields": subfields_dict,
                "original_line": line
            }
        )

    def read_subfields(self, subfields_data, field):
        subfields_data = subfields_data.strip()
        subfields_list = subfields_data.split('$')
        subfields_dict = OrderedDict()
        for subfield_string in subfields_list:
            if not subfield_string:
                continue
            subfield = subfield_string[:1]
            if not subfield:
                continue
            subfield_content = subfield_string[1:]
            subfield_content = subfield_content.strip()
            if self.loose_rules is True:
                # skip second $a fields
                if subfield == "8" and "8" in subfields_dict:
                    continue
            self.check_subfield(subfield, subfield_content,
                                subfields_dict, field)
            subfields_dict[subfield] = subfield_content
        return subfields_dict


class Convert85x86x(Read85x86x):
    """
    Function to do the actual work of converting 85x/86x lines.
    """

    full_output = namedtuple("Full86xOutput", "holdings nonpublic_note public_note original_line")

    def __init__(self, input_str):
        super().__init__(input_str)

        self.links = {
            '853': {},
            '854': {},
            '855': {}
        }
        self.current_link = None
        self.output_strings = []  # just holdings strings, when found
        self.output_strings_with_notes = []  # namedtuple of holdings strings and 2 sorts of notes for all fields
        self.read_field_dicts()

    def read_field_dicts(self):
        last_field = ""
        for field_dict in self.holdings_lines:
            if field_dict["field"] in self.fields_85x:
                if last_field == "86x":
                    self.links = {'853': {}, '854': {}, '855': {}}
                self.read_85x(field_dict)
                last_field = "85x"
            elif field_dict["field"] in self.fields_86x:
                self.convert_86x(field_dict)
                last_field = "86x"

    def read_85x(self, field_dict):
        self.check_85x_line(field_dict)
        self.current_link = field_dict["subfields"]["8"]
        self.links[field_dict["field"]][self.current_link] = {}
        self.read_caption_subfields(field_dict["subfields"], field_dict["field"])

    def read_caption_subfields(self, subfields, field):
        for caption_subfield_type in self.caption_subfield_types:
            for subfield in self.caption_subfields[caption_subfield_type]:
                if subfield in subfields:
                    self.links[field][self.current_link][subfield] = subfields[subfield]

    def convert_86x(self, field_dict):
        self.check_86x_line(field_dict)
        formatted_string = self.read_86x_field_labels(field_dict)
        if formatted_string:
            if field_dict["field"] == "864" and 'supp' not in formatted_string.lower():
                formatted_string = "suppl " + formatted_string
            elif field_dict["field"] == "865":
                formatted_string = "index " + formatted_string
            self.output_strings.append(formatted_string)
        nonpublic_note, public_note = self.get_86x_notes(field_dict)
        self.output_strings_with_notes.append(self.full_output(formatted_string, nonpublic_note, public_note,
                                                               field_dict['original_line']))

    @staticmethod
    def get_86x_notes(field_dict):
        """Extract notes from the 86x field $x and $z, if they exist"""
        try:
            nonpublic_note = field_dict['subfields']['x']
        except KeyError:
            nonpublic_note = ''
        try:
            public_note = field_dict['subfields']['z']
        except KeyError:
            public_note = ''
        return nonpublic_note, public_note

    def read_86x_field_labels(self, field_dict):
        labeled_subfields = {
            'enumeration': OrderedDict(),
            'secondary_enumeration': OrderedDict(),
            'chronology': OrderedDict()
        }
        field_link = field_dict['subfields']['8'].split('.')[0]
        self.current_link = field_link
        for subfield_type in self.caption_subfield_types:
            for subfield in self.caption_subfields[subfield_type]:
                self.get_subfield_label(subfield_type, subfield, field_dict, labeled_subfields)
        enumeration_string = self.make_enumeration(labeled_subfields)
        secondary_enumeration_string = self.make_enumeration(labeled_subfields, enumeration_type='secondary_enumeration')
        chronology_string = self.make_enumeration(labeled_subfields, 'chronology')

        if enumeration_string:
            if secondary_enumeration_string:
                enumeration_string = "{} ({})".format(enumeration_string, secondary_enumeration_string)
            if chronology_string:
                return "{} ({})".format(enumeration_string, chronology_string)
            else:
                return enumeration_string
        elif chronology_string:
            return "({})".format(chronology_string)
        return ""

    def get_subfield_label(self, subfield_type, subfield, field_dict, labeled_subfields):
        link_field = self.fields_86x_to_85x[field_dict["field"]]
        if subfield not in field_dict['subfields']:
            return
        try:
            if subfield not in self.links[link_field][self.current_link]:
                warning_str = f"subfield {subfield} from 86x not in 85x"
                self.add_warning_message(warning_str)
                return
        except KeyError:
            error_str = f"subfield {subfield} from 86x not in 85x"
            self.add_warning_message(error_str)
        try:
            label = self.links[link_field][self.current_link][subfield]
        except KeyError:
            error_str = f"Field link {self.current_link} from {link_field} $8 not found"
            self.add_warning_message(error_str)
            return
        subfield_content = field_dict["subfields"][subfield]
        if label.startswith('+'):
            subfield_content = self.number_string_to_ordinal(subfield_content)
        if "month" in label:
            subfield_content = self.convert_chronology_digits_string_to_text(
                "months", subfield_content)
        elif "season" in label:
            subfield_content = self.convert_chronology_digits_string_to_text(
                "seasons", subfield_content)
        content_list = subfield_content.split('-', 1)
        self.check_for_too_many_dashes_in_enumeration_or_chronology(
            content_list, subfield_content)
        labeled_subfields[subfield_type][label] = content_list

    def make_enumeration(self, labeled_subfields, enumeration_type='enumeration'):
        chronology_tuple = namedtuple("ChronologyTuple", "value, label")
        enumeration_lists = [
            [], []
        ]
        # continuing refers to a continued holding, something like "v.5- "
        continuing = False
        chronology_segments = []
        for label in labeled_subfields[enumeration_type]:
            spacer = ""
            if not label.endswith('.'):
                spacer = " "
            enum_segments = labeled_subfields[enumeration_type][label]
            if label.startswith('('):
                if '*' not in label and enumeration_type != "secondary_enumeration":
                    tup = chronology_tuple(enum_segments, label)
                    chronology_segments.append(tup)
                    continue
                elif self.loose_rules and label == "(no.)":
                    label = "no."
                elif enumeration_type != "secondary_enumeration":
                    label = re.sub("[()]", "", label)
                    label = re.sub("(?:year|month|season)", "", label)
                else:
                    label = ''
            for i in range(0, len(enum_segments)):
                segment_data = enum_segments[i]
                if not segment_data:
                    continuing = True
                else:
                    if label.startswith('+'):
                        segment_data = "{}{}{}".format(segment_data, " ", label[1:])
                    elif label:
                        segment_data = "{}{}{}".format(label, spacer, segment_data)
                    enumeration_lists[i].append(segment_data)
        enumeration_string_1 = ':'.join(enumeration_lists[0])
        enumeration_string_2 = ':'.join(enumeration_lists[1])
        enumeration_str = ""
        if enumeration_lists[1]:
            enumeration_str = "{}-{}".format(enumeration_string_1, enumeration_string_2)
            enumeration_str = self.remove_extra_enumeration_labels(enumeration_str)
        else:
            enumeration_str = enumeration_string_1
        if continuing:
            enumeration_str += '-'

        if chronology_segments:
            parenthesis_string = self.chronology_segments_to_output(chronology_segments)
            if enumeration_str:
                enumeration_str = "{} {}".format(enumeration_str, parenthesis_string)
            else:
                enumeration_str = parenthesis_string

        # cleanup
        return enumeration_str

    @staticmethod
    def remove_extra_enumeration_labels(enumeration_str):
        if '-' not in enumeration_str:
            return enumeration_str
        no_or_number = r'(?:no\.?|num\.?)'
        pt_or_part = r'(?:pt\.?|part)'
        numbers = r'\d+(?:/\d+)?'
        enumeration_str = re.sub(r"({}{}-){}({})$".format(no_or_number, numbers, no_or_number, numbers), r'\1\2', enumeration_str)
        enumeration_str = re.sub(r"({}{}-){}({})$".format(pt_or_part, numbers, pt_or_part, numbers), r'\1\2', enumeration_str)
        return enumeration_str

    def chronology_segments_to_output(self, chronology_segments):
        # TODO: At the moment this ignores labels, which are in position 2 in the input tuple
        continuing = False
        # Assume that top level of these will be year, which should always be last      
        year_seg_tuple = chronology_segments.pop(0)
        year_seg = year_seg_tuple[0]
        if len(year_seg) > 1 and not year_seg[-1]:
            continuing = True
            year_seg.pop(-1)
        tracks = [[], []]

        # only years
        if len(chronology_segments) == 0:
            return_string = '-'.join(year_seg)
            if continuing is True:
                return_string += '- '
            return return_string

        for segment_tuple in chronology_segments:
            segment = segment_tuple[0]
            for i in range(0, len(segment)):
                if segment[i]:
                    tracks[i].append(segment[i])
        year_1 = ""
        year_2 = ""
        if '/' in year_seg[0]:
            year_1 = year_seg[0]
        if len(year_seg) == 2 and '/' in year_seg[1]:
            year_1 = year_seg[0]
            year_2 = year_seg[1]
        slash_string_1 = self.make_slash_divided_chronology_tracks(tracks[0], year_1)
        slash_string_2 = self.make_slash_divided_chronology_tracks(tracks[1], year_2)

        join_character_1 = ", "
        join_character_2 = ", "
        if len(tracks[0]) == 1:
            join_character_1 = " "
        if len(tracks[1]) == 1:
            join_character_2 = " "

        if not year_2 and len(year_seg) == 2:
            slash_string_2 = "{}{}{}".format(slash_string_2, join_character_2, year_seg[1])
            if not year_1:
                slash_string_1 = "{}{}{}".format(slash_string_1, join_character_1, year_seg[0])

        slash_string = ""

        if slash_string_2:
            slash_string = "{}-{}".format(slash_string_1, slash_string_2)
        else:
            slash_string = slash_string_1

        if not year_1:
            if not slash_string:
                slash_string = year_seg[0]
            else:
                if not re.search(r"\d\d\d\d-.*\d\d\d\d", slash_string):
                    slash_string = "{}{}{}".format(slash_string, join_character_1, year_seg[0])
                else:
                    pass
        if continuing is True:
            slash_string += '- '
        return slash_string

    @staticmethod
    def make_slash_divided_chronology_tracks(track, year):
        """
        Convert a list like "['Sep', 'Sep/Oct'], ['18/24', '30/07']" to a string like "Sep 18/24-Sep 30/Oct 07"
        """
        year_slashes = year.split('/', 1)
        slash_tracks = [[], []]
        seen_slashes = False
        for i in range(0, len(track)):
            if '/' not in track[i]:
                slash_tracks[0].append(track[i])
            elif seen_slashes is False and i == len(track)-1:
                slash_tracks[0].append(track[i])
            else:
                seen_slashes = True
                subsegments = track[i].split('/', 1)
                for n in range(0, len(subsegments)):
                    slash_tracks[n].append(subsegments[n])
        join_character_1 = ", "
        join_character_2 = ", "
        if slash_tracks[0] and len(slash_tracks[0]) == 1:
            join_character_1 = " "
        if slash_tracks[1] and len(slash_tracks[1]) == 1:
            join_character_2 = " "

        for i in range(0, len(slash_tracks)):
            slash_tracks[i] = " ".join(slash_tracks[i])
        if slash_tracks[1]:
            if not year_slashes[0]:
                pass
            elif len(year_slashes) == 2:
                slash_tracks[0] = "{}{}{}".format(slash_tracks[0], join_character_1, year_slashes[0])
                slash_tracks[1] = "{}{}{}".format(slash_tracks[1], join_character_2, year_slashes[1])
            elif len(year_slashes) == 1:
                slash_tracks[1] = "{}{}{}".format(slash_tracks[1], join_character_2, year_slashes[0])
            return "/".join(slash_tracks)
        elif slash_tracks[0]:
            if not year_slashes[0]:
                pass
            elif len(year_slashes) == 2:
                slash_tracks[0] = "{}{}{}-{}".format(slash_tracks[0], join_character_1, year_slashes[0], year_slashes[1])
            elif len(year_slashes) == 1:
                slash_tracks[0] = "{}{}{}".format(slash_tracks[0], join_character_1, year_slashes[0])
            return slash_tracks[0]
        elif year:
            return year
        return ""

    def convert_chronology_digits_string_to_text(self, chronology_type, chronology_digits_str):
        if re.search("[^0-9-/]", chronology_digits_str):
            if self.loose_rules is False:
                self.add_warning_message("Invalid months data {}".format(chronology_digits_str))
        chronology_str = chronology_digits_str
        digits_list = re.findall(r"(\d+)", chronology_digits_str)
        for digits in digits_list:
            chron_data = ""
            if chronology_type == "months":
                chron_data = self.convert_month_number_to_text(digits)
            elif chronology_type == "seasons":
                chron_data = self.convert_season_number_to_text(digits)
            else:
                warning_str = "Unkonwn chronlogy label: {}".format(chronology_type)
                self.add_warning_message(warning_str)
                return chronology_digits_str
            try:
                chronology_str = re.sub(r"(\b){}(\b)".format(digits), r"\1{}\2".format(chron_data), chronology_str)
            except re.error:
                print(f"CHRON TYPE: {chronology_type}\tDIGITS: {digits}\tCHRON DATA: {chron_data}\tCHRON STRING: {chronology_str}")

        return chronology_str

    def convert_season_number_to_text(self, season_number):
        try:
            return self.seasons[season_number]
        except KeyError:
            if self.loose_rules is True:
                try:
                    return self.loose_seasons[season_number]
                except KeyError:
                    try:
                        return self.months[int(season_number)]
                    except (IndexError, ValueError):
                        pass
            self.add_warning_message("Invalid season number of {}".format(season_number))
            return season_number

    def convert_month_number_to_text(self, month_number):
        try:
            return self.months[int(month_number)]
        except IndexError:
            if self.loose_rules is True:
                try:
                    return self.seasons[month_number]
                except KeyError:
                    try:
                        return self.loose_seasons[month_number]
                    except KeyError:
                        pass
        except ValueError:
            if self.loose_rules is True:
                # allow something like "Sept" as month_num
                return month_number
            pass
        self.add_warning_message("Invalid month number of {}".format(month_number))
        return month_number

    def number_string_to_ordinal(self, number_str):
        number_str_list = re.findall(r"(\d+)", number_str)
        for number in number_str_list:
            ordinal_string = self.number_to_ordinal(number)
            number_str = number_str.replace(number, ordinal_string, 1)
        return number_str

    def number_to_ordinal(self, n):
        """
        Convert an integer into its ordinal representation::

            make_ordinal(0)   => '0th'
            make_ordinal(3)   => '3rd'
            make_ordinal(122) => '122nd'
            make_ordinal(213) => '213th'

        Note that the bulk of this function was pulled off of Stack Overflow.
        """
        try:
            n = int(n)
        except (TypeError, ValueError):
            warning_text = f"Text to be turned into ordinal is not a number: {n}"
            self.add_warning_message(warning_text)
            return n
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        if 11 <= (n % 100) <= 13:
            suffix = 'th'
        return str(n) + suffix
