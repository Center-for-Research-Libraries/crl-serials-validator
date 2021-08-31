"""
Work with the locally installed ISSN database. 

Either the crl_prefs module must be present and the ISSN database in one of the locations specified in the 
CrlFileLocations class, or the path to the local copy of the database must be set in the LOCAL_ISSN_DB_FILE_LOCATION 
variable.

Basic usage:
    from crl_lib.issn_db import IssnDb

    issn_db = IssnDb()
    marc_string_for_issn_a = issn_db.get_marc_from_issn_a(issn_a) 
    marc_string_for_issn_a = issn_db.get_marc_from_issn_db(issn)
    marc_list_for_issn_y = issn_db.get_marc_from_issn_y(issn_y)
    dict_of_sets_of_marc_by_issn_type = issn_db.get_marc_from_issn_db_any_issn_type(any_issn)

The ISSN database has a somewhat unusual title format, that doesn't match exactly to a standard MARC 245. Usually what
is here called "title_a" will approximate the 245 title, but if not the additional "title_b" often will

    title_a, title_b = issn_db.get_titles_from_issn_marc(issn_db_marc)

To run basic tests on the module, just run the file as a script with the -t flag:

    python issn_db.py -t

To print ISSN MARC data to the screen, run the script with an ISSN afterwards:

    python issn_db.py 0000-1775

"""
import re
import sys
import sqlite3
import os
import argparse
from pprint import pprint

# Set the following variable to identify a specific path for a local install of the ISSN db.
# Leave it as None if the crl_prefs module is installed locally and the db is at an expected location.
LOCAL_ISSN_DB_FILE_LOCATION = None


class IssnDb:
    def __init__(self, ignore_missing_db=False):

        self.found_issn_db = False
        self.__issn_db_location = None

        if LOCAL_ISSN_DB_FILE_LOCATION:
            self.__issn_db_location = LOCAL_ISSN_DB_FILE_LOCATION
        else:
            try:
                from crl_lib.crl_prefs import CrlFileLocations
            except ModuleNotFoundError or ImportError:
                msg = 'local_issn_db_file_location variable not set and crl_prefs module not found.\n'
                msg += 'ISSN database cannot be found. Quitting.'
                print(msg, file=sys.stderr)
                sys.exit()

            crl_files = CrlFileLocations()
            self.__issn_db_location = crl_files.issn_db_file_location

        error_message = ''
        if not self.__issn_db_location:
            self.found_issn_db = False
            if not ignore_missing_db:
                error_message = 'No ISSN database location specified? Quitting.'
        elif not os.path.isfile(self.__issn_db_location):
            self.found_issn_db = False
            if not ignore_missing_db:
                error_message = 'ISSN database not found at location {}'.format(
                    self.__issn_db_location)
        else:
            self.found_issn_db = True
            self.conn = sqlite3.connect(self.__issn_db_location)

        if error_message:
            sys.exit('Error: {}'.format(error_message))

    def __del__(self):
        """
        Gracefully close the db on script termination.
        """
        try:
            self.conn.close()
        except AttributeError:
            # Attribute error if the db was not found in the first place.
            pass

    def close_db(self):
        """
        Close the database.
        """
        self.conn.close()

    @staticmethod
    def get_titles_from_issn_marc(marc):
        """
        The ISSN database has an unusual title format. This function approximates a standard 245 title from an ISSN db 
        title.
        """
        title_a = None
        title_b = None
        title_222_a = None
        title_222_b = None
        title_245_a = None
        title_245_b = None

        m = re.search(r"=222 [^\r\n]*\$a([^\r\n$]*)", marc)
        if m is not None:
            title_222_a = m.group(1)
            m2 = re.search(r"=222 [^\r\n]*\$b([^\r\n$]*)", marc)
            if m2 is not None:
                title_222_b = m2.group(1)

        m = re.search(r"=245 [^\r\n]*\$a([^\r\n$]*)", marc)
        if m is not None:
            title_245_a = m.group(1)
            m2 = re.search(r"=245 [^\r\n]*\$b([^\r\n$]*)", marc)
            if m2 is not None:
                title_245_b = m2.group(1)

        if title_222_a is not None:
            title_a = title_222_a
            title_b = title_222_b
        elif title_245_a is not None:
            title_a = title_245_a
            title_b = title_245_b

        return title_a, title_b

    def get_marc_from_issn_db_any_issn_type(self, issn):
        """
        Get all associated MARC from a lot of different ISSN types. 

        Returns a dict by type, each dict being a set of MARC records. This is likely to be a somewhat awkward format, 
        so it will often be easier to search by specific ISSN types if you know what you are looking for. Also as this 
        does five queries per run, specific searches will likely be faster. 
        """
        marc_dict = {'issn_a': set(), 'issn_l': set(), 'issn_y': set(),
                     'issn_z': set(), 'issn_m': set(), 'valid_issn': None}
        if not issn:
            raise Exception('No ISSN sent to function.')

        marc_dict['valid_issn'] = check_for_valid_issn(issn)
        new_marc_a = self.get_marc_from_issn_a(issn)
        if new_marc_a:
            marc_dict['issn_a'] = set([new_marc_a])
        new_marc_l = self.get_marc_from_issn_l(issn)
        marc_dict['issn_l'] = set(new_marc_l)
        new_marc_y = self.get_marc_from_issn_y(issn)
        marc_dict['issn_y'] = set(new_marc_y)
        new_marc_z = self.get_marc_from_issn_z(issn)
        marc_dict['issn_z'] = set(new_marc_z)
        new_marc_m = self.get_marc_from_issn_m(issn)
        marc_dict['issn_m'] = set(new_marc_m)
        return marc_dict

    def get_issns_from_issn_type(self, other_issn, issn_type):
        if issn_type == 'issn' or issn_type == 'issn_a':
            marc = self.get_marc_from_issn_a(other_issn)
            return [marc]
        table = '{}_to_issn'.format(issn_type)
        c = self.conn.cursor()
        c.execute("SELECT issn FROM {} WHERE {} == '{}'".format(
            table, issn_type, other_issn.upper()))
        issn_tuples = c.fetchall()
        issns = set()
        for issn_tuple in issn_tuples:
            issns.add(issn_tuple[0])
        return list(issns)

    def get_marc_from_issn_db(self, issn_a):
        """Old function name, kept for compatibility with existing scripts."""
        marc = self.get_marc_from_issn_a(issn_a)
        return marc

    def get_marc_from_issn(self, issn_a):
        """Old function name, kept for compatibility with existing scripts."""
        marc = self.get_marc_from_issn_a(issn_a)
        return marc

    def get_marc_from_issn_variant(self, issn_variant, issn_type):
        table_name = '{}_to_issn'.format(issn_type)
        select_sql = 'SELECT marc FROM marc_records INNER JOIN {} ON {}.issn = marc_records.issn WHERE {} == ?'.format(
            table_name, table_name, issn_type
        )
        c = self.conn.cursor()
        c.execute(select_sql, (issn_variant.upper(),))
        marc_tuples = c.fetchall()
        marc = []
        for marc_tuple in marc_tuples:
            marc.append(marc_tuple[0])
        return marc

    def get_marc_from_issn_a(self, issn_a):
        statement = "SELECT marc FROM marc_records WHERE issn = ?"
        c = self.conn.cursor()
        c.execute(statement, (issn_a.upper(),))
        try:
            c_tuple = c.fetchall()
            if len(c_tuple) > 1:
                raise Exception(
                    'More than one MARC record in database for ISSN {}. Bad database?'.format(issn_a))
            return c_tuple[0][0]
        except IndexError:
            return ''

    def get_marc_from_issn_l(self, issn_l):
        marc = self.get_marc_from_issn_variant(issn_l, 'issn_l')
        return marc

    def get_marc_from_issn_y(self, issn_y):
        marc = self.get_marc_from_issn_variant(issn_y, 'issn_y')
        return marc

    def get_marc_from_issn_z(self, issn_z):
        marc = self.get_marc_from_issn_variant(issn_z, 'issn_z')
        return marc

    def get_marc_from_issn_m(self, issn_m):
        marc = self.get_marc_from_issn_variant(issn_m, 'issn_m')
        return marc


def check_for_valid_issn(issn):
    """
    Check if an ISSN-type string is a legal ISSN.

    The last character is a check digit. Algorithm:
        1. Multiply first digit by 8, second by 7, etc to seventh by 2. Add the sums up.
        2. Take modulus 11 of the total. If modulus is 0 then check digit should be 0.
        3. Otherwise subtract the modulus from 11. This will be check digit, with 'X' standing for 10.

    This duplicates the function in the standard crl_lib, but that one first attempts to fix poorly formed ISSNs. (So 
    "15865" would be formatted to "0001-5865" before checking.)
    """
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


def parse_command_line_arguments():
    parser_description = 'Module to extract data from the ISSN database. '
    parser_description += 'Usually just the IssnDb class will be used from within another script.'
    parser = argparse.ArgumentParser(description=parser_description)
    parser.add_argument('--test', '-t', action='store_true', help='run the modules tests' )
    parser.add_argument('--t', action='store_true', help='run the modules tests' )
    parser.add_argument('-i', type=str, help='Optional ISSN type. Valid types are a, l, m, y, or z')
    parser.add_argument('ISSN', nargs='*')
    args = parser.parse_args()
    if args.test:
        args.t = True
    if args.i and args.i.lower() not in {'a', 'l', 'm', 'y', 'n'}:
        raise Exception("Argument -a must be a, l, m, y, or z.")
    return args


def run_tests():
    """
    Testing function.

    Note that if a test fails it's possible that changes to the database have made one or more of the test ISSNs invalid 
    or inaccurate. So the database should probably be checked by hand, just in case.
    """
    print('Running tests on issn_db.py')

    test_issns = {
        'issn_a': '2064-7182',
        'issn_l': '0001-4370',
        'issn_m': '0044-2216',
        'issn_y': '0000-1775',
        'issn_z': '0567-7807',
        'valid_issn_not_in_database': '9999-9994',
        'invalid_issn': '9999-9993',
    }

    issn_db = IssnDb()

    if not issn_db.found_issn_db:
        raise Exception('ISSN database not found.')

    for issn_type in test_issns:
        issn = test_issns[issn_type]
        print('----------------------------------------')
        print('ISSN: {}'.format(issn))
        print('Type: {}'.format(issn_type))
        issn_dict = issn_db.get_marc_from_issn_db_any_issn_type(issn)
        pprint(issn_dict)
        if issn_type in issn_dict and len(issn_dict[issn_type]) == 0:
            raise Exception('Nothing found for {} search.'.format(issn_type))
        elif issn_type == 'invalid_issn' and issn_dict['valid_issn'] is True:
            raise Exception(
                'Invalid ISSN {} identified as valid.'.format(issn))
        elif issn_type == 'valid_issn_not_in_database':
            if issn_dict['valid_issn'] is False:
                raise Exception(
                    'Valid ISSN {} identified as invalid.'.format(issn))
            for issn_type in ['issn_a', 'issn_l', 'issn_m', 'issn_y', 'issn_z']:
                if len(issn_dict[issn_type]) != 0:
                    msg = 'ISSN of type {} found for what should be blank ISSN {}'.format(
                        issn_type, issn)
                    raise Exception((msg))
    print('All tests passed.')


def app():
    """
    Either run the test suite, or get MARC from ISSNs.
    """
    args = parse_command_line_arguments()
    if args.t:
        run_tests()
    else:
        issn_db = IssnDb()
        for issn in args.ISSN:
            if args.i:
                print('')
                print(issn)
                issn_type = 'issn_{}'.format(args.i.lower())
                marc_data = issn_db.get_issns_from_issn_type(issn, issn_type)
                for marc_record in marc_data:
                    print(marc_record)
            else:
                marc_data_dict = issn_db.get_marc_from_issn_db_any_issn_type(issn)
                print(issn)
                print('valid_issn: {}'.format(marc_data_dict['valid_issn']))
                issn_types = ['issn_a', 'issn_l', 'issn_m', 'issn_y', 'issn_z']
                for issn_type in issn_types:
                    if len(marc_data_dict[issn_type]) > 0:
                        print('{} {}'.format(issn, issn_type))
                        print('')
                        for marc in marc_data_dict[issn_type]:
                            print(marc)


if __name__ == '__main__':
    app()
