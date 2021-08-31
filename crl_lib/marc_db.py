"""
Legacy script, do not use for new development.
"""

import sqlite3
import os

from crl_lib.crl_data_paths import find_marc_collection_file, find_marc_db_files


def open_marc_db():
    dbfile, fail_file, report_file = find_marc_db_files()
    # should return None on other machines
    if not os.path.isfile(dbfile):
        return None
    if dbfile is not None:
        conn = sqlite3.connect(dbfile)
        return conn
    else:
        raise ValueError('MARC database file not found')


def close_db(conn):
    conn.close()


def find_correct_oclc(conn, oclc):
    if oclc is None:
        return
    try:
        oclc = int(oclc)
    except:
        return
    c = conn.cursor()
    t = (oclc,)
    c.execute('SELECT oclc_number FROM oclcs_019 WHERE oclc_019 == ?', t)
    return c.fetchone()


def marc_from_db_via_oclc(conn, oclc, recent_only=False):
    # TODO: add recent-only exception
    try:
        oclc = int(oclc)
    except:
        return
    if recent_only is True:
        statement = "SELECT marc FROM marc_records JOIN oclcs_019 USING (oclc_number) WHERE oclc_019 = ? AND DATE('now', '-1 year') < updated_date"
    else:
        statement = "SELECT marc FROM marc_records JOIN oclcs_019 USING (oclc_number) WHERE oclc_019 = ?"
    t = (oclc, )
    c = conn.cursor()
    c.execute(statement, t)
    try:
        c_tuple = c.fetchone()
        return c_tuple[0]
    except:
        return


# do everything with an OCLC
def marc_from_db_full(oclc, recent_only=False):
    try:
        oclc = int(oclc)
    except:
        return
    conn = open_marc_db()
    if conn:
        marc = marc_from_db_via_oclc(conn, oclc, recent_only)
        close_db(conn)
        if marc:
            return marc
        else:
            return None


# ------------------------------------------------------------------------------


def marc_to_marc_collection(marc):
    if not marc:
        return
    if "=LDR" not in marc:
        return
    _print_to_marc_collection_file(marc)


# ------------------------------------------------------------------------------


def remove_marc_from_db_by_oclc(oclcs):
    try:
        if int(oclc) > 99999999999:
            return
    except:
        return
    conn = open_marc_db()
    c = conn.cursor()
    statement = "DELETE FROM marc_records WHERE oclc_number == ?"
    statement_oclcs_019 = "DELETE FROM oclcs_019 WHERE oclc_019 == ?"
    t = (oclc, )
    try:
        c.execute(statement, t)
        c.execute(statement_oclcs_019, t)
        conn.commit()
    except:
        pass
    conn.close()

# ------------------------------------------------------------------------------


def _print_to_marc_collection_file(marc):
    collection_file = find_marc_collection_file()
    if not collection_file:
        return
    fout = open(collection_file, 'a', encoding="utf8")
    fout.write(marc + "\n\n")
