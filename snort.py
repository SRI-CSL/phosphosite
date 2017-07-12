#!/usr/bin/env python

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


url = "http://www.phosphosite.org/simpleSearchSubmitAction.action?queryId=-1&from=0&searchStr={0}"


def firstLink(p):
    f =  urllib2.urlopen(url.format(p))
    html_doc = f.read()

    soup = BeautifulSoup(html_doc, 'html.parser')

    #print(soup.prettify())


    return soup.find_all('a', class_='link13HoverRed')[0]  #first element looks to be the one we want.


for p in proteins:
    print p, '\t', firstLink(p)
