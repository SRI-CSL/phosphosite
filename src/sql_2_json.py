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


conn = sqlite3.connect('../db/phosphosite_full.sqlite')


extract_proteins(conn, database_0)
dump_database(database_0, 'proteins_sql.json')

extract_sites(conn, database_1)
dump_database(database_1, 'sites_sql.json')

extract_controls(conn, database_2)
dump_database(database_2, 'controls_sql.json')
