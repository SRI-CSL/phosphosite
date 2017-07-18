#!/usr/bin/env python

import re
import urllib2
import sys

#pip install beautifulsoup4
import bs4


import sqlite3

proteins = [
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


conn = sqlite3.connect('../db/phophosite.sqlite')
cursor = conn.cursor()




# we are going to build three databases.

#this maps our protein name (string element of list above) to it's phosphosite id
database_0 = {}

#this maps the phosposite id to the set (as a list) of 'Sites implicated in'
database_1 = {}


#this maps the site implicated id to the 'controlled by' data.
database_2 = {}


def dump_database(database, name):
    with open(name, "w") as dbf:
        dbstr = repr(database)
        dbf.write(dbstr.replace("'", '"'))

url_1 = "http://www.phosphosite.org/simpleSearchSubmitAction.action?queryId=-1&from=0&searchStr={0}"



idPattern = re.compile('id=(\d*)')

# the first looks to be the one we want. but we could pattern match if that fails.
# do the simple minded thing first.
#<a class="link13HoverRed" href="/../proteinAction.action?id=2791&amp;showAllSites=true">human</a>
#http://www.phosphosite.org/proteinAction.action?id=2791&showAllSites=true
def firstLink(p):
    f =  urllib2.urlopen(url_1.format(p))
    html_doc = f.read()

    soup = bs4.BeautifulSoup(html_doc, 'html.parser')

    #print(soup.prettify())

    candidate = soup.find_all('a', class_='link13HoverRed')[0] #first element looks to be the one we want.

    sys.stderr.write('.')

    match = idPattern.search(str(candidate))

    if match:
        retval = match.group(1)
    else:
        retval = '-1'

    return int(retval)

# turn off, temporarily, while we have the data below.
if False:
    for p in proteins:
        #print '# {0}\n{1},'.format(p, firstLink(p))
        database_0[p] =  firstLink(p)
        dump_database(database_0, "protein_ids.json")
        sys.stderr.write('\n')
        #from which we deduce we get


protein_ids = [
    # AKT1
    570,
    # APC
    3867,
    # ATF1
    3541,
    # ATR
    576,
    # BIM
    2791,
    # BRAF
    577,
    # CHEK2
    468,
    # CREB1
    1489,
    # FAK1
    598,
    # GATA3
    7977,
    # HSPB1
    989,
    # IGFBP2
    22867,
    # IRS1
    855,
    # JUN
    943,
    # MTOR
    564,
    # PDCD4
    4192,
    # PLK1
    648,
    # PRAS40
    22501100,
    # RAF1
    653,
    # RASGRP1
    7848,
    # SETD8
    13600,
    # STAT1
    1048,
    # STAT3
    1050,
    # TP53BP1
    3129,
    # TTK
    779,
    # YBX1
    2629,
]


#url_2 = 'http://www.phosphosite.org/proteinAction.action?id={0}&showAllSites=true'
url_2 = 'http://www.phosphosite.org/proteinModificationSitesDomainsAction.action?id={0}&showAllSites=true'

#deprecated
#def secondLink(pid, accumulator):
#    f =  urllib2.urlopen(url_2.format(pid))
#    html_doc = f.read()
#
#    soup = bs4.BeautifulSoup(html_doc, 'html.parser')
#
#    candidates =  soup.find_all('a', href=re.compile('siteAction'))
#    for c in candidates:
#        match = idPattern.search(str(c))
#        if match:
#            accumulator.add(match.group(1))


#<a href="/../siteAction.action?id=2885">T308\u2011p</a>

if False:
    for pid in protein_ids:
        sys.stderr.write('.')
        result = set()
        secondLink(pid, result)
        database_1['{0}'.format(pid)] = list(result)
        #print '\n# ', 10 * '-', pid, 10 * '-', '\n\n', result
    dump_database(database_1, "sites_implicated.json")
    sys.stderr.write('\n')




def processSecondLinkTds(tds, hmap):
    for td in tds:
        anchors = td.find_all('a')
        if anchors:
            key = td.text.encode('ascii', 'ignore').lstrip()
            colon = key.find(":")
            if colon != -1:
                key = key[0:colon]
            else:
                key = key.rstrip()
            results = {}
            hmap[key] = results
            for a in anchors:
                akey = a.text.encode('ascii', 'ignore').strip()
                match = idPattern.search(str(a))
                if match:
                    results[akey] = match.group(1)
    #print hmap


def second2Link(pid, hmap):
    f =  urllib2.urlopen(url_2.format(pid))
    html_doc = f.read()

    soup = bs4.BeautifulSoup(html_doc, 'html.parser')

    target = soup.find_all('td', text='Sites Implicated In ')
    if target:
        target = target[0].parent.parent
        target = target.contents[3].find_all('table')[0]
        tds = target.find_all('td', attrs={"colspan": 3})
        processSecondLinkTds(tds, hmap)

#http://www.phosphosite.org/proteinAction.action?id=3867&showAllSites=true
#hmap = {}
#second2Link(3867, hmap)

if True:
    for pid in protein_ids:
        sys.stderr.write('.')
        result = {}
        second2Link(pid, result)
        database_1['{0}'.format(pid)] = result
        #print '\n# ', 10 * '-', pid, 10 * '-', '\n\n', result
    dump_database(database_1, "sites_implicated.json")
    sys.stderr.write('\n')


url_3 = 'http://www.phosphosite.org/siteAction.action?id={0}'

#http://www.phosphosite.org/siteAction.action?id=2886


def processSpans(td, references, results, category):
    hmap = {}
    cval = None
    for child in td.contents:
        if isinstance(child, bs4.element.NavigableString):
            continue
        if child.name == 'span':
            cval = []
            key = str(child.text).replace(' (human)', '').replace("'", '') #5'-methylthioadenosine (1)
            hmap[key] = cval
        else:
            cval.append(references[int(child.text)])
    return hmap


def processTds(pid, tds, references, results, fails):
    num = 0
    category = ''
    while tds:
        num += 1
        #print 'td_{0}'.format(num), tds[0]
        #print 'td_{0}.text'.format(num), tds[0].text
        category = str(tds[0].text)
        num += 1
        #print 'td_{0}'.format(num), tds[1]
        #print 'td_{0}.spans.text'.format(num), [ str(x.text).replace(' (human)', '') for x in tds[1].find_all('span') ]
        #print 'td_{0}.anchors.text'.format(num), [ int(x.text) for x in tds[1].find_all('a') ]
        #print 'td_{0}.references'.format(num), [ references[int(x.text)] for x in tds[1].find_all('a') ]
        spans = processSpans(tds[1], references, results, category)
        if spans:
            results[category] = spans
        else:
            print 'Nyet'
            fails[pid] = True
        #results[category] = ([ str(x.text).replace(' (human)', '') for x in tds[1].find_all('span') ], [ references[int(x.text)] for x in tds[1].find_all('a') ])

        tds = tds[2:]


def getReferences(soup):
    references = {}
    anchors = soup.find_all('a',class_="anchor",href=re.compile('#top'))
    refs = []
    for anchor in anchors:
        refs.append((anchor, anchor.parent.parent.parent))
    for ref in refs:
        try:
            #print ref[0].text
            #print ref[1].find(href=re.compile("https://www.ncbi.nlm.nih.gov/")).text
            references[int(ref[0].text)] = str(ref[1].find(href=re.compile("https://www.ncbi.nlm.nih.gov/")).text)
        except:
            #print ref[0].text
            #print ref[1]
            pass

    return references


fails = { }
done = { }

def thirdLink(pid, database_2, fails):
    f =  urllib2.urlopen(url_3.format(pid))
    html_doc = f.read()

    results = {}
    database_2[pid] = results

    soup = bs4.BeautifulSoup(html_doc, 'html.parser')

    #ok get the references too.
    references = getReferences(soup)

    candidate = soup.find_all('td', string=re.compile('Controlled by '))  #
    if candidate:
        candidate = candidate[0].parent.parent #get the containing table.
        #navigate down to the
        candidate = candidate.contents[3]
        candidate = candidate.contents[1]
        candidate = candidate.contents[1]
        tds = candidate.find_all('td')
        processTds(pid, tds, references, results, fails)
    else:
        fails[pid] = True
        print 'Nope'

#deprecated
#if False:
#    for key in database_1:
#        for pid in database_1[key]:
#            if not pid in database_2:
#                if pid not in fails:
#                    sys.stderr.write('.')
#                    thirdLink(pid, database_2, fails)
#                else:
#                    print 'Failure'
#        sys.stderr.write('\n')
#    #print database_2
#    dump_database(database_2, "controlled_by.json")


if True:
    sys.stderr.write('on to database_2\n')
    for key in database_1:
        d = database_1[key]
        for skey in d:
            for site in d[skey]:
                pid = d[skey][site]
                if pid not in fails:
                    if pid not in done:
                        sys.stderr.write('.')
                        thirdLink(pid, database_2, fails)
                        done[pid] = True
                else:
                    print 'Failure'
        sys.stderr.write('\n')
    dump_database(database_2, "controlled_by.json")



#http://www.phosphosite.org/siteAction.action?id=2886
#thirdLink(2886, database_2, fails)


#for pid in ['8086746', '7817075', '8086742', '5665', '9231', '33182', '34498197', '58948825', '2226713', '3803', '34503491', '21567', '34503136', '31089431', '9908975', '2226532', '9229', '9228', '59789', '2945', '21546', '12723410', '5862772', '2882', '2886', '8086740', '31888028', '2885', '9230', '2888', '2889', '22075952', '4994', '34349789', '22075951', '28706801', '28706800', '46993', '33178', '5862776', '3189785', '3804', '3802', '22075955', '3805', '3227664', '22776840', '40216700', '8086730', '8086736', '8086734', '5663', '46992', '4675', '50772861', '9908969', '12723406', '25537905', '25537904', '25537903', '25537902', '9232', '9233', '17546661', '31089432', '5664', '14515800', '4261100', '4261103', '4261102', '29714', '15384324', '14515802', '22776834', '22776837', '5660', '3822706', '29711', '23080892', '22075954']:
#    thirdLink(pid)
