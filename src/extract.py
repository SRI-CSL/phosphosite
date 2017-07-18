#!/usr/bin/env python

import re
import sys
import sqlite3


# extracts the database out into the "desired" json

# we are going to build three json databases.

#this maps our protein name to it's phosphosite id
database_0 = {}

#this maps the phosposite id to the dictionary of 'Sites implicated in'
database_1 = {}

#this maps the site implicated id to the 'controlled by' data.
database_2 = {}


#at some stage we should learn to pretty print this puppy rather than doing the json lint web thing.
def dump_database(database, name):
    with open(name, "w") as dbf:
        dbstr = repr(database)
        dbf.write(dbstr.replace("'", '"'))



conn = sqlite3.connect('../db/phosphosite.sqlite')


def process_proteins(conn, db):
    cursor = conn.cursor()
    cursor.execute('SELECT name, phosphosite_id FROM protein')
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        db[str(row[0])] = row[1]
    dump_database(db, 'proteins_sql.json')



def process_sites(conn, db):
    pass


def process_controls(conn, db):
    pass


process_proteins(conn, database_0)
process_sites(conn, database_1)
process_controls(conn, database_0)
