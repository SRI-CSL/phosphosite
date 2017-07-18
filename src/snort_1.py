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
        cursor.execute('INSERT INTO protein (name, phosphosite_id) VALUES(?, ?)', [name, pid])
    else:
        cursor.execute('INSERT INTO protein_fail (name) VALUES(?)', [name])

    conn.commit()

    return pid






def process_protein(conn, name):

    pid = get_protein_id(conn, name)

    print '{0}  has id {1}\n'.format(name, pid)

    result_set = process_site(conn, pid)

    for spid in result_set:
        process_control(conn, pid, spid)

    # mark it as done
    conn.cursor().execute('INSERT INTO site_success (phosphosite_id) VALUES(?)', [str(pid)])





url_2 = 'http://www.phosphosite.org/proteinModificationSitesDomainsAction.action?id={0}&showAllSites=true'


def secondLink(conn, pid, result_set):
    f =  urllib2.urlopen(url_2.format(pid))
    html_doc = f.read()

    soup = bs4.BeautifulSoup(html_doc, 'html.parser')

    target = soup.find_all('td', text='Sites Implicated In ')
    if target:
        target = target[0].parent.parent
        target = target.contents[3].find_all('table')[0]
        tds = target.find_all('td', attrs={"colspan": 3})
        processSecondLinkTds(conn, pid, tds, result_set)

def processSecondLinkTds(conn, pid, tds, result_set):
    for td in tds:
        anchors = td.find_all('a')
        if anchors:
            key = td.text.encode('ascii', 'ignore').lstrip()
            colon = key.find(":")
            if colon != -1:
                key = key[0:colon]
            else:
                key = key.rstrip()
            for a in anchors:
                match = idPattern.search(str(a))
                if match:
                    site = a.text.encode('ascii', 'ignore').strip()
                    val = match.group(1)
                    result_set.add(val)
                    put_site(conn, pid, key, site, match.group(1))


def put_site(conn, pid, category, site, val):
    cursor = conn.cursor()
    sys.stderr.write('put_site(pid={0}, category={1}, site={2}, val={3})\n'.format(pid, category, site, val))
    category_id = get_site_category_id(conn, category)
    site_id = get_site_name_id(conn, site)
    cursor.execute('INSERT INTO site (site_pid, site_category_id, site_name_id, phosphosite_id) VALUES(?,?,?,?)', [pid, category_id, site_id, val])


def process_site(conn, pid):

    cursor = conn.cursor()

    #if is has failed previously skip it
    cursor.execute('SELECT * FROM site_fail WHERE phosphosite_id=?', [str(pid)])
    if cursor.fetchone() is not None:
        sys.stderr.write('sites for {0} have already failed\n'.format(pid))
        return None

    #if it has succeeded previously skip it
    cursor.execute('SELECT * FROM site_success WHERE phosphosite_id=?', [str(pid)])
    if cursor.fetchone() is not None:
        sys.stderr.write('sites for {0} have already succeeded\n'.format(pid))
        return None

    #no excuses better do it.
    result_set = set()

    secondLink(conn, pid, result_set)

    sys.stderr.write('processed sites for {0} got:\n{1}!\n'.format(pid, list(result_set)))

    conn.commit()

    return result_set


def get_site_name_id(conn, name):
    cursor = conn.cursor()
    cursor.execute('SELECT site_name_id FROM site_name WHERE name=?', [name])
    snid = cursor.fetchone()
    if snid is not None:
        return int(snid[0])
    cursor.execute('INSERT INTO site_name (name) VALUES(?)', [name])
    return int(cursor.lastrowid)


def get_site_category_id(conn, category):
    cursor = conn.cursor()
    cursor.execute('SELECT site_category_id FROM site_category WHERE name=?', [category])
    scid = cursor.fetchone()
    if scid is not None:
        return int(scid[0])
    cursor.execute('INSERT INTO site_category (name) VALUES(?)', [category])
    return int(cursor.lastrowid)


def get_control_name_id(conn, name):
    cursor = conn.cursor()
    cursor.execute('SELECT control_name_id FROM control_name WHERE name=?', [name])
    snid = cursor.fetchone()
    if snid is not None:
        return int(snid[0])
    cursor.execute('INSERT INTO control_name (name) VALUES(?)', [name])
    return int(cursor.lastrowid)




def process_control(conn, pid, spid):
    sys.stderr.write('processing controls for {0} by {1}!\n'.format(pid, spid))



for protein in protein_list:
    print 'name = {0}'.format(protein)
    process_protein(conn, protein)



conn.close()
