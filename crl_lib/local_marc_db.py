import sqlite3
import os
import datetime

from crl_lib.marc_fields import WorldCatMarcFields


class LocalMarcDb:
    """
    Class for interacting with the local SQLite MARC database.

    This will likely mostly be used through a WorldCat API fetcher class like 
    WcApi in crl_lib.wc_api.

    Basic usage, for fetching records:

        from crl_lib.local_marc_db import LocalMarcDb()

        db = LocalMarcDb()
        marc_record = db.get_marc_from_db

    WorldCat MARC records as strings or lists of strings can be added to the 
    database, like this:

        from crl_lib.local_marc_db import LocalMarcDb()

        db = LocalMarcDb()
        db.collect_data_for_marc_db(worldcat_marc)

    For project-specific work, the database file location can be overridden like so:

        db = LocalMarcDb("/path/to/file")

    """
    def __init__(self, data_folder):
        if not data_folder:
            raise Exception('No data folder location sent to local_marc_db')
        self.marc_collection_db_file_location = os.path.join(data_folder, 'marc_collection.db')
        
        self.timestamp = self.make_year_month_day_timestamp()
        # default SQL commands
        self.marc_record_insert = 'INSERT OR REPLACE INTO marc_records (oclc_number, issn, updated_date, marc) ' \
                                  'VALUES (?, ?, ?, ?)'
        self.oclc_number_insert = 'INSERT OR REPLACE INTO oclcs_019 (oclc_019, oclc_number) VALUES (?, ?)'
        self.old_oclc_delete = 'DELETE FROM marc_records WHERE oclc_number == ?'

        # Default save data lists
        self.marc_insert_data = []
        self.oclc_insert_data = []
        self.oclc_delete_data = []

        # open database, and create it if it doesn't already exist
        if os.path.isfile(self.marc_collection_db_file_location):
            self.conn = sqlite3.connect(self.marc_collection_db_file_location)
        else:
            self.conn = sqlite3.connect(self.marc_collection_db_file_location)
            self.create_local_marc_db()

        self.main_table_has_issn_column = self._check_for_issn_column()

    def __del__(self):
        """
        Destructor, to commit any unsaved changes to the MARC database and to 
        close it gracefully.
        """
        if self.marc_insert_data:
            self._write_collected_data_to_marc_db()
        self.close_marc_db()

    @staticmethod
    def make_year_month_day_timestamp():
        """Get a timestamp in the form YYYY-MM-DD"""
        d = datetime.datetime.now()
        timestamp = d.strftime("%Y-%m-%d")
        return timestamp

    def _write_collected_data_to_marc_db(self):
        if len(self.marc_insert_data) == 0:
            return
        c = self.conn.cursor()
        c.executemany(self.marc_record_insert, self.marc_insert_data)
        c.executemany(self.oclc_number_insert, self.oclc_insert_data)
        c.executemany(self.old_oclc_delete, self.oclc_delete_data)
        self.conn.commit()
        self._reset_save_lists()

    def _reset_save_lists(self):
        """Zero out the save lists."""
        self.marc_insert_data = []
        self.oclc_insert_data = []
        self.oclc_delete_data = []

    def _check_for_issn_column(self):
        """Old version of the database might not have a column for issns"""
        c = self.conn.cursor()
        c.execute('PRAGMA table_info(marc_records)')
        pragma_tuples = c.fetchall()
        for pragma_tuple in pragma_tuples:
            if pragma_tuple[1] == 'issn':
                return True

        self.marc_record_insert = 'INSERT OR REPLACE INTO marc_records (oclc_number, updated_date, marc) ' \
                                  'VALUES (?, ?, ?)'
        return False

    def close_marc_db(self):
        try:
            self.conn.close()
        except AttributeError:
            pass

    def create_local_marc_db(self):
        """
        If a local MARC db isn't present in the user's data folder, create
        one for data storage.
        """
        create_marc_records_table_sql = 'CREATE TABLE "marc_records" (oclc_number INTEGER UNIQUE, issn TEXT, '\
                                        'updated_date DATE, marc TEXT NOT NULL, PRIMARY KEY (oclc_number));'
        create_oclcs_019_table_sql = 'CREATE TABLE oclcs_019 (oclc_019 INTEGER NOT NULL UNIQUE, oclc_number INTEGER ' \
                                     'NOT NULL, PRIMARY KEY (oclc_019));'
        c = self.conn.cursor()
        c.execute(create_marc_records_table_sql)
        c.execute(create_oclcs_019_table_sql)
        self.conn.commit()

    def find_correct_oclc(self, oclc):
        try:
            oclc = int(oclc)
        except TypeError:
            return
        except ValueError:
            return
        c = self.conn.cursor()
        t = (oclc,)
        c.execute('SELECT oclc_number FROM oclcs_019 WHERE oclc_019 == ?', t)
        return c.fetchone()

    def get_marc_from_db(self, oclc, recent_only=False):
        # TODO: add recent-only exception
        try:
            oclc = int(oclc)
        except (TypeError, ValueError):
            return
        if recent_only is True:
            statement = "SELECT marc FROM marc_records JOIN oclcs_019 USING (oclc_number) WHERE oclc_019 = ? AND " \
                        "DATE('now', '-1 year') < updated_date"
        else:
            statement = "SELECT marc FROM marc_records JOIN oclcs_019 USING (oclc_number) WHERE oclc_019 = ?"
        t = (oclc, )
        c = self.conn.cursor()
        c.execute(statement, t)
        try:
            c_tuple = c.fetchone()
            return c_tuple[0]
        except TypeError:
            return

    def collect_data_for_marc_db(self, marc):
        """
        Data collector, generally to be invoked via a fetcher like that in the
        wc_api library. The input can be either a MARC record as a string, or a
        list of MARC records as strings.

        Usage:

            marc_db = LocalMarcDb()
            marc_db.collect_data_for_marc_db(worldcat_marc_record)

        """

        if not marc:
            return
        if type(marc) == str:
            marc = [marc]
        for marc_record in marc:
            mf = WorldCatMarcFields(marc_record)
            oclc = mf.oclc
            old_oclcs = mf.oclcs_019
            issn = mf.issn_a

            if self.main_table_has_issn_column is True:
                marc_insert_data_tuple = (oclc, issn, self.timestamp, marc_record)
            else:
                marc_insert_data_tuple = (oclc, self.timestamp, marc_record)

            self.marc_insert_data.append(marc_insert_data_tuple)

            self.oclc_insert_data.append((oclc, oclc))
            for old_oclc in old_oclcs:
                self.oclc_insert_data.append((old_oclc, oclc))
                self.oclc_delete_data.append((old_oclc, ))

        if len(self.marc_insert_data) > 100:
            self._write_collected_data_to_marc_db()
            self._reset_save_lists()


def marc_from_db_full(oclc, recent_only=False):
    """Get MARC with only an OCLC, without previously opening the database."""
    db = LocalMarcDb()
    marc = db.get_marc_from_db(oclc, recent_only)
    return marc
