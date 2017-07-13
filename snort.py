#!/usr/bin/env python

import re
import urllib2

#pip install beautifulsoup4
from bs4 import BeautifulSoup


proteins = [
    'AKT1',
    'APC',
    'ATF1',
    'ATR',
    'BIM',
    'BRAF',
    'CHEK2',
    'CREB1',
    'FAK1',
    'GATA3',
    'HSPB1',
    'IGFBP2',
    'IRS1',
    'JUN',
    'MTOR',
    'PDCD4',
    'PLK1',
    'PRAS40',
    'RAF1',
    'RASGRP1',
    'SETD8',
    'STAT1',
    'STAT3',
    'TP53BP1',
    'TTK',
    'YBX1',
]


url_1 = "http://www.phosphosite.org/simpleSearchSubmitAction.action?queryId=-1&from=0&searchStr={0}"



idPattern = re.compile('id=(\d*)')

# the first looks to be the one we want. but we could pattern match if that fails.
# do the simple minded thing first.
#<a class="link13HoverRed" href="/../proteinAction.action?id=2791&amp;showAllSites=true">human</a>
#http://www.phosphosite.org/proteinAction.action?id=2791&showAllSites=true
def firstLink(p):
    f =  urllib2.urlopen(url_1.format(p))
    html_doc = f.read()

    soup = BeautifulSoup(html_doc, 'html.parser')

    #print(soup.prettify())

    candidate = soup.find_all('a', class_='link13HoverRed')[0] #first element looks to be the one we want.


    print candidate

    match = idPattern.search(str(candidate))

    if match:
        retval = match.group(1)
    else:
        retval = None

    return retval

# turn off, temporarily, while we have the data below.
if False:
    for p in proteins:
        print '# {0}\n{1},'.format(p, firstLink(p))

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

def secondLink(pid, accumulator):
    f =  urllib2.urlopen(url_2.format(pid))
    html_doc = f.read()

    soup = BeautifulSoup(html_doc, 'html.parser')

    candidates =  soup.find_all('a', href=re.compile('siteAction'))
    for c in candidates:
        match = idPattern.search(str(c))
        if match:
            accumulator.add(match.group(1))


#<a href="/../siteAction.action?id=2885">T308\u2011p</a>

if False:
    for pid in protein_ids:
        result = set()
        secondLink(pid, result)
        print '\n# ', 10 * '-', pid, 10 * '-', '\n\n', result



url_3 = 'http://www.phosphosite.org/siteAction.action?id={0}'


categories = [
    'Regulatory protein',
    'Putative upstream phosphatases',
    'Phosphatases',
    'Treatments',
    ]

def thirdLink(pid):
    f =  urllib2.urlopen(url_3.format(pid))
    html_doc = f.read()

    soup = BeautifulSoup(html_doc, 'html.parser')

    candidate = soup.find_all('td', string=re.compile('Controlled by '))  #
    if candidate:
        candidate = candidate[0].parent.parent #get the containing table.
        print(candidate.prettify()) #soup.prettify())
    else:
        print 'Nope'


#http://www.phosphosite.org/siteAction.action?id=2886
thirdLink(2886)
