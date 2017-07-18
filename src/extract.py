#!/usr/bin/env python

import re
import sys
import sqlite3

# our local utilities
from sql_aux import *

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


def process_site_row(db, row):
    pass

def process_sites(conn, db):
    cursor = conn.cursor()
    site_query = '''
    SELECT s.site_pid, sc.name, sn.name, s.phosphosite_id
    FROM site AS s, site_category AS sc, site_name AS sn
    WHERE s.site_category_id = sc.site_category_id AND  s.site_name_id = sn.site_name_id
    '''
    cursor.execute(site_query)
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        process_site_row(row, db)
    dump_database(db, 'sites_sql.json')

def process_control_row(db, row):
    pass


def process_controls(conn, db):
    cursor = conn.cursor()
    control_query = '''
    SELECT c.phosphosite_id, cc.name, cn.name, c.controller
    FROM control AS c, control_category AS cc, control_name AS cn
    WHERE c.control_category_id = cc.control_category_id AND  c.control_name_id = cn.control_name_id
    '''
    cursor.execute(control_query)
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        process_control_row(row, db)
    dump_database(db, 'controls_sql.json')


process_proteins(conn, database_0)
process_sites(conn, database_1)
process_controls(conn, database_2)
