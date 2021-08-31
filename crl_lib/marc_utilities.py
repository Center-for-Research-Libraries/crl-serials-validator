import re
import sys


def get_field_subfield_position(record, field, subfield=None, position=None):
    """
    Find a subfield and or position in a field.
    Can search for a position in a field or subfield.
    Leaving subfield blank searches for entire contents of the field.
    Leaving position blank returns entire field/subfield.
    Returns a list.
    """
    if subfield:
        regex = "=" + str(field) + r"  .*\$" + subfield + r'([^\$\\r\\n]+)'
    else:
        regex = "=" + str(field) + r"  ([^\\r\\n]+)"
    initial_results = re.findall(regex, record)
    if not position:
        return initial_results
    results = []
    position = int(position)
    position_plus = position
    position_plus += 1
    for initial_result in initial_results:
        position_data = initial_result[position:position_plus]
        if position_data:
            results.append(position_data)
    return results


def get_field_subfield(record, field, subfield=None):
    """
    Find a single subfield in a single field.
    Leaving subfield blank searches for entire contents of the field.

    Usage:

        main_title = get_field_subfield(marc_record, "245", "a")

    Can also deal with strings like "245" for the 245$a, passed as the field only.
    """
    if not field or not record:
        return ''
    if len(field) == 4:
        field, subfield = get_field_subfield_from_joined_string(field)
    if subfield:
        regex = "=" + str(field) + r"\s\s.*\$" + subfield + r'([^\$\r\n]+)'
    else:
        regex = "=" + str(field) + r"\s\s([^\r\n]+)"
    try:
        m = re.search(regex, record)
    except RecursionError:
        return ''
    try:
        subfield_data = m.group(1)
        return subfield_data
    except AttributeError:
        return ''


def get_fields_subfields(record, field, subfield=None):
    """
    Find a all instances of a subfield in all instances of a field.
    Leaving subfield blank searches for entire contents of the field.

    Usage:

        subject_term_list = get_fields_subfields(marc_record, "650", "a")

    Can also deal with strings like "245" for the 245$a, passed as the field only.
    """
    if not field:
        return ''
    if len(field) == 4:
        field, subfield = get_field_subfield_from_joined_string(field)
    found_fields = re.findall(r"={}\s\s([^\r\n]+)".format(field), record)
    if not subfield:
        return found_fields

    return_data = []
    for found_field in found_fields:
        m = re.findall(r"\${}([^$]+)".format(subfield), found_field)
        for subfield_data in m:
            return_data.append(subfield_data)
    
    return return_data


def get_segments_of_marc_record(record, split_field):
    """
    Splits a record on a field and returns the segments found after the first value of the field.
    This is usually to find holdings segments (i.e., all fields between 852 lines.)
    Note that splitting on "LDR" will return an empty list.
    """
    
    if not record:
        sys.exit("Record not specified in get_segment_of_marc_record function.")
    if not split_field:
        sys.exit("Split field not specified in get_segment_of_marc_record function.")
    split_record_list = record.split("={}  ".format(split_field))
    marc_segments = split_record_list[1:]
    for i in range(0, len(marc_segments)):
        marc_segments[i] = "={}  {}".format(split_field, marc_segments[i])
    return marc_segments


def get_field_subfield_from_joined_string(field_subfield):
    """Turn something like '245a' into '245' and 'a'."""
    if len(field_subfield) == 3:
        subfield = ""
    elif len(field_subfield) == 4:
        subfield = field_subfield[3:]
    else:
        raise Exception("Bad field/subfield submitted? Submitted {}".format(field_subfield))
    field = field_subfield[:3]
    if check_valid_field(field) is True:
        return field, subfield
    raise Exception("Bad field/subfield submitted? Submitted {}".format(field_subfield))


def check_valid_field(field):
    if field and len(str(field)) == 3:
        try:
            int(field)
            return True
        except ValueError:
            if field == "LDR":
                return True
        return False
