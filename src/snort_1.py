#!/usr/bin/env python

import re
import urllib2
import sys

#pip install beautifulsoup4
import bs4


import sqlite3


url_1 = "http://www.phosphosite.org/simpleSearchSubmitAction.action?queryId=-1&from=0&searchStr={0}"


idPattern = re.compile('id=(\d*)')


protein_list = [
    "AKT1",
    "APC",
    "ATF1",
    "ATR",
    "BIM",
    "BRAF",
    "CHEK2",
    "CREB1",
    "FAK1",
    "GATA3",
    "HSPB1",
    "IGFBP2",
    "IRS1",
    "JUN",
    "MTOR",
    "PDCD4",
    "PLK1",
    "PRAS40",
    "RAF1",
    "RASGRP1",
    "SETD8",
    "STAT1",
    "STAT3",
    "TP53BP1",
    "TTK",
    "YBX1",
]

#'http://www.phosphosite.org/simpleSearchSubmitAction.action?queryId=-1&from=0&searchStr="AKT1"'

conn = sqlite3.connect('../db/phosphosite.sqlite')


def get_protein_id(conn, name):

    cursor = conn.cursor()

    #step one: see if it is already in the protein table
    cursor.execute('SELECT name, phosphosite_id FROM protein WHERE name=?', [name])
    answer = cursor.fetchone()
    if answer is not None:
        (name, pid) = answer
        return pid
    else:
        #need to check the fail table
        cursor.execute('SELECT * FROM protein_fail WHERE name=?', [name])
        if cursor.fetchone() is not None:
            return -1

    #step two: see if we can find it from the phosphosite site (if necessary)
    pid = -1
    url = url_1.format(name)
    f =  urllib2.urlopen(url)
    html_doc = f.read()
    soup = bs4.BeautifulSoup(html_doc, 'html.parser')
    candidate = soup.find_all('a', class_='link13HoverRed')
    if candidate:
        candidate = candidate[0] #first element looks to be the one we want.
    sys.stderr.write('.')
    match = idPattern.search(str(candidate))
    if match:
        pid = int(match.group(1))


    #step three: update the table to reflect the status
    insert_query = 'INSERT INTO protein (name, phosphosite_id) VALUES(?)'
    if pid != -1:
        cursor.execute('INSERT INTO protein (name, phosphosite_id) VALUES(?, ?)', (name, pid))
    else:
        cursor.execute('INSERT INTO protein_fail (name) VALUES(?)', (name))

    conn.commit()

    return pid


def process_protein(conn, name):

    pid = get_protein_id(conn, name)

    print '{0}  has id {1}\n'.format(name, pid)


for protein in protein_list:
    print 'name = {0}'.format(protein)
    process_protein(conn, protein)



conn.close()
