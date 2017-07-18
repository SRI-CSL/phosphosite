import sqlite3



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
