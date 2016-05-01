import datetime
import pandas as pd

import psycopg2
import sys


def get_ratings():
    conn = psycopg2.connect("dbname='prs' user='postgres' password='sa'")
    ratings = pd.read_sql('select * from ratings', conn)

    return ratings

def save_similarity_from_df(df, created=datetime.datetime.now(), version=1):
    print("Save item-item model")

    similarities = list()
    for row in df.iterrows():
        source = int(row[0])
        target = int(row[1].values[0])
        sim = float(row[1].values[1])

        if not target == source and sim > 0:
            similarities.append((created, source, target, sim, version))
    save_cf(similarities)

def save_cf(similarities):
    con = None

    try:
        con = psycopg2.connect("dbname='prs' user='postgres' password='sa'")

        cur = con.cursor()
        cur.executemany("INSERT INTO public.cf_similarity(created, source, target, similarity, version)" +
                        "VALUES (%s::timestamp, %s::numeric, %s::numeric, %s::numeric, %s::numeric);",
                        similarities)

        con.commit()

    except psycopg2.DatabaseError as e:
        if con:
            con.rollback()

        print('Error %s' % e)
        sys.exit(1)

    finally:

        if con:
            con.close()
