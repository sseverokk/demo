import psycopg2

DB_CONFIG = {
    'database': "mydb",
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
            SELECT
                p.id,
                pt.name,
                p.name_partner,
                p.director,
                p.tel,
                p.rating
            FROM partners p
            JOIN partner_types pt ON pt.id = p.type_id
            ORDER BY p.name_partner;
        """)
        return cur.fetchall()


def get_partner(partner_id):
    with get_connection() as con:
        cur = con.cursor()
        cur.execute("""
            SELECT id, type_id, name_partner, director,
                   email, tel, adres, inn, rating
            FROM partners
            WHERE id = %s;
        """, (partner_id,))
        return cur.fetchone()


def insert_partner(data):
    with get_connection() as con:
        cur = con.cursor()
        cur.execute("""
            INSERT INTO partners
                (type_id, name_partner, director, email,
                 tel, adres, inn, rating)
            VALUES
                (%(type_id)s, %(name_partner)s, %(director)s, %(email)s,
                 %(tel)s, %(adres)s, %(inn)s, %(rating)s);
        """, data)


def update_partner(partner_id, data):
    d = dict(data)
    d["id"] = partner_id
    with get_connection() as con:
        cur = con.cursor()
        cur.execute("""
            UPDATE partners
            SET type_id=%(type_id)s,
                name_partner=%(name_partner)s,
                director=%(director)s,
                email=%(email)s,
                tel=%(tel)s,
                adres=%(adres)s,
                inn=%(inn)s,
                rating=%(rating)s
            WHERE id=%(id)s;
        """, d)


def delete_partner(partner_id):
    with get_connection() as con:
        cur = con.cursor()
        cur.execute("DELETE FROM partners WHERE id=%s;", (partner_id,))


def fetch_sales_history(partner_id):
    with get_connection() as con:
        cur = con.cursor()
        cur.execute("""
            SELECT
                s.sale_date,
                p.name,
                si.quantity
            FROM sales s
            JOIN sale_items si ON si.sale_id = s.id
            JOIN products p ON p.id = si.product_id
            WHERE s.partner_id = %s
            ORDER BY s.sale_date DESC;
        """, (partner_id,))
        return cur.fetchall()