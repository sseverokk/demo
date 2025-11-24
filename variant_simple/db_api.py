import psycopg2

DB_CONFIG = {
    'database': "mydb2",
    'user': 'admin',
    'password': '12345',
    'host': 'localhost',
    'port': 5432
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def fetch_partner_types():
    with get_connection() as con:
        cur = con.cursor()
        cur.execute("SELECT id, name FROM partner_types ORDER BY name;")
        return cur.fetchall()

def fetch_partners():
    with get_connection() as con:
        cur = con.cursor()
        cur.execute("""
            SELECT p.id, t.name, p.name_partner, p.director, p.tel, p.rating
            FROM partners p
            JOIN partner_types t ON t.id = p.type_id
            ORDER BY p.name_partner;
        """)
        return cur.fetchall()

def get_partner(pid):
    with get_connection() as con:
        cur = con.cursor()
        cur.execute("""
            SELECT id, type_id, name_partner, director,
                   email, tel, adres, inn, rating
            FROM partners WHERE id = %s;
        """, (pid,))
        return cur.fetchone()

def insert_partner(data):
    with get_connection() as con:
        cur = con.cursor()
        cur.execute("""
            INSERT INTO partners 
                (type_id, name_partner, director, email, tel, adres, inn, rating)
            VALUES 
                (%(type_id)s, %(name_partner)s, %(director)s, %(email)s,
                 %(tel)s, %(adres)s, %(inn)s, %(rating)s);
        """, data)

def update_partner(pid, data):
    data["id"] = pid
    with get_connection() as con:
        cur = con.cursor()
        cur.execute("""
            UPDATE partners
            SET type_id=%(type_id)s, name_partner=%(name_partner)s,
                director=%(director)s, email=%(email)s, tel=%(tel)s,
                adres=%(adres)s, inn=%(inn)s, rating=%(rating)s
            WHERE id=%(id)s;
        """, data)

def delete_partner(pid):
    with get_connection() as con:
        cur = con.cursor()
        cur.execute("DELETE FROM partners WHERE id=%s;", (pid,))