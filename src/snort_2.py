#!/usr/bin/env python


import sqlite3

# our local utilities
from sql_aux import *

conn = sqlite3.connect('../db/phosphosite_full.sqlite')

# 19K proteins
protein_list = file2list('../data_in/hgnc.txt')


count = 0
for protein in protein_list:
    print '{0}: name = {1}'.format(count, protein)
    count += 1
    #process_protein(conn, protein)

conn.close()
