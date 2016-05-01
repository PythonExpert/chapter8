import datetime
import os
import pandas as pd
import psycopg2
from unittest import TestCase

import database
from src.item_cf_builder import build


class TestBuilder(TestCase):
    version = 199923

    def test_save_mini_ratings(self):

        number_of_similarities = 38

        conn = psycopg2.connect("dbname='prs' user='postgres' password='sa'")
        ratings = pd.read_sql('select * from ratings')

        try:
            build(ratings, self.version)

            saved_rows = self.count_rows_with_version(self.version)

            self.assertEquals(number_of_similarities, saved_rows[0])

        finally:
            self.clean_db()

    def test_save_cf(self):

        timestamp = datetime.datetime.now()  # '2014-05-01T13:00:00+00:00'

        items = list()
        items.append((timestamp, 1, 2, 4.3453, self.version))

        database.save_cf(items)

        self.clean_db()

    def count_rows_with_version(self, version):
        count = 0
        con = None
        try:
            con = psycopg2.connect("dbname='prs' user='postgres' password='sa'")

            cur = con.cursor()

            cur.execute("SELECT COUNT(1) FROM public.cf_similarity WHERE version = %s;" % self.version)
            count = cur.fetchone()

        except Exception as e:
            self.fail(e)

        finally:
            con.close()

        return count

    def clean_db(self):
        con = None
        try:
            con = psycopg2.connect("dbname='prs' user='postgres' password='sa'")

            cur = con.cursor()

            cur.execute("DELETE FROM public.cf_similarity WHERE version = %s;" % self.version)
            #con.commit()
        except Exception as e:
            self.fail(e)

        finally:
            con.close()

    def test_frozen_sets(self):
        frozens = set()
        frozens.add(frozenset({1,2}))

        if not frozenset({1,2}) in frozens:
            self.fail("should be in set")
        if not frozenset({2,1}) in frozens:
            self.fail("should be in set")