import re
import urllib2
import sys

#pip install beautifulsoup4
import bs4


import sqlite3


idPattern = re.compile('id=(\d*)')


def file2list(path):
    retval = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                retval.append(line)
    return retval


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
    url_1 = "http://www.phosphosite.org/simpleSearchSubmitAction.action?queryId=-1&from=0&searchStr={0}"
    url = url_1.format(name)
    f =  urllib2.urlopen(url)
    print url
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

def set_protein_fail(conn, name):
    conn.cursor().execute('INSERT INTO protein_fail (name) VALUES(?)', [str(name)])



def process_protein(conn, name):
    pid = get_protein_id(conn, name)
    print '{0}  has id {1}\n'.format(name, pid)
    if int(pid) < 0:
        set_protein_fail(conn, name)
    else:
        result_set = process_site(conn, pid)
        if result_set:
            for spid in result_set:
                process_control(conn, spid)
                # mark it as done
        set_site_success(conn, pid)



def secondLink(conn, pid, result_set):
    url_2 = 'http://www.phosphosite.org/proteinModificationSitesDomainsAction.action?id={0}&showAllSites=true'
    url = url_2.format(pid)
    f =  urllib2.urlopen(url)
    html_doc = f.read()
    soup = bs4.BeautifulSoup(html_doc, 'html.parser')
    print url
    #print soup.prettify()
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
    #sys.stderr.write('put_site(pid={0}, category={1}, site={2}, val={3})\n'.format(pid, category, site, val))
    category_id = get_site_category_id(conn, category)
    site_id = get_site_name_id(conn, site)
    cursor.execute('INSERT INTO site (site_pid, site_category_id, site_name_id, phosphosite_id) VALUES(?,?,?,?)', [pid, category_id, site_id, val])


def process_site(conn, pid):
    #if is has failed previously skip it
    if is_site_fail(conn, pid):
        sys.stderr.write('sites for {0} have already failed\n'.format(pid))
        return None
    #if it has succeeded previously skip it
    if is_site_success(conn, pid):
        sys.stderr.write('sites for {0} have already succeeded\n'.format(pid))
        return None
    #no excuses better do it.
    result_set = set()
    secondLink(conn, pid, result_set)
    sys.stderr.write('processed sites for {0} got:\n{1}!\n'.format(pid, list(result_set)))
    conn.commit()
    return result_set


def process_control(conn, pid):
    sys.stderr.write('processing controls for {0}!\n'.format(pid))
    #if is has failed previously skip it
    if is_control_fail(conn, pid):
        sys.stderr.write('controls for {0} have already failed\n'.format(pid))
        return None
    #if it has succeeded previously skip it
    if is_control_success(conn, pid):
        sys.stderr.write('controls for {0} have already succeeded\n'.format(pid))
        return None
    thirdLink(conn, pid)
    # mark it as done
    set_control_success(conn, pid)
    conn.commit()


def thirdLink(conn, pid):
    url_3 = 'http://www.phosphosite.org/siteAction.action?id={0}'
    f =  urllib2.urlopen(url_3.format(pid))
    html_doc = f.read()
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
        processTds(conn, pid, tds, references)
    else:
        # mark it as failed
        set_control_fail(conn, pid)

def getReferences(soup):
    references = {}
    anchors = soup.find_all('a',class_="anchor",href=re.compile('#top'))
    refs = []
    for anchor in anchors:
        refs.append((anchor, anchor.parent.parent.parent))
    for ref in refs:
        try:
            references[int(ref[0].text)] = str(ref[1].find(href=re.compile("https://www.ncbi.nlm.nih.gov/")).text)
        except:
            pass
    return references

def put_control(conn, pid, category, name, val):
    cursor = conn.cursor()
    category_id = get_control_category_id(conn, category)
    name_id = get_control_name_id(conn, name)
    cursor.execute('INSERT INTO control (phosphosite_id, control_category_id, control_name_id, controller) VALUES(?,?,?,?)', [pid, category_id, name_id, val])

def processSpans(conn, pid, td, references, category):
    for child in td.contents:
        if isinstance(child, bs4.element.NavigableString):
            continue
        if child.name == 'span':
            key = str(child.text).replace(' (human)', '').replace("'", '') #5'-methylthioadenosine (1)
        else:
            put_control(conn, pid, category, key, references[int(child.text)])


def processTds(conn, pid, tds, references):
    num = 0
    category = ''
    while tds:
        num += 1
        category = str(tds[0].text)
        num += 1
        processSpans(conn, pid, tds[1], references, category)
        tds = tds[2:]


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

def is_site_fail(conn, pid):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM site_fail WHERE phosphosite_id=?', [str(pid)])
    if cursor.fetchone() is not None:
        return True
    return False

def is_site_success(conn, pid):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM site_success WHERE phosphosite_id=?', [str(pid)])
    if cursor.fetchone() is not None:
        return True
    return False

def set_site_fail(conn, pid):
    conn.cursor().execute('INSERT INTO site_fail (phosphosite_id) VALUES(?)', [str(pid)])

def set_site_success(conn, pid):
    conn.cursor().execute('INSERT INTO site_success (phosphosite_id) VALUES(?)', [str(pid)])

def get_control_category_id(conn, name):
    cursor = conn.cursor()
    cursor.execute('SELECT control_category_id FROM control_category WHERE name=?', [name])
    snid = cursor.fetchone()
    if snid is not None:
        return int(snid[0])
    cursor.execute('INSERT INTO control_category (name) VALUES(?)', [name])
    return int(cursor.lastrowid)

def get_control_name_id(conn, name):
    cursor = conn.cursor()
    cursor.execute('SELECT control_name_id FROM control_name WHERE name=?', [name])
    snid = cursor.fetchone()
    if snid is not None:
        return int(snid[0])
    cursor.execute('INSERT INTO control_name (name) VALUES(?)', [name])
    return int(cursor.lastrowid)

def is_control_fail(conn, pid):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM control_fail WHERE phosphosite_id=?', [str(pid)])
    if cursor.fetchone() is not None:
        return True
    return False

def is_control_success(conn, pid):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM control_success WHERE phosphosite_id=?', [str(pid)])
    if cursor.fetchone() is not None:
        return True
    return False

def set_control_fail(conn, pid):
    conn.cursor().execute('INSERT INTO control_fail (phosphosite_id) VALUES(?)', [str(pid)])

def set_control_success(conn, pid):
    conn.cursor().execute('INSERT INTO control_success (phosphosite_id) VALUES(?)', [str(pid)])
