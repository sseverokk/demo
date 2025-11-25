import psycopg2

config_admin = {
    'database': "postgres",
    'user': 'postgres',
    'password': '200610',
    'host': 'localhost',
    'port': 5432
}

config = {
    'database': "mydb2",
    'user': 'admin',
    'password': '12345',
    'host': 'localhost',
    'port': 5432
}

def db_create():
    con = psycopg2.connect(**config_admin)
    con.autocommit = True
    cur = con.cursor()

    cur.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='admin') THEN
                CREATE USER admin WITH PASSWORD '12345' LOGIN;
            END IF;
        END
        $$;
    """)

    cur.execute("SELECT 1 FROM pg_database WHERE datname='mydb2';")
    if not cur.fetchone():
        cur.execute("CREATE DATABASE mydb2 WITH OWNER admin ENCODING 'UTF8';")

    cur.close()
    con.close()


def load_data():
    with psycopg2.connect(**config) as con:
        cur = con.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS partner_types (
                id   SERIAL PRIMARY KEY,
                name VARCHAR(50) NOT NULL
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS partners (
                id           SERIAL PRIMARY KEY,
                type_id      INT NOT NULL REFERENCES partner_types(id),
                name_partner VARCHAR(255) NOT NULL,
                director     VARCHAR(255),
                email        VARCHAR(255),
                tel          VARCHAR(50),
                adres        TEXT,
                inn          BIGINT,
                rating       NUMERIC(6,2) DEFAULT 0
            );
        """)

        cur.execute("""
            INSERT INTO partner_types (name)
            VALUES ('Оптовый'), ('Розничный'), ('Онлайн');
        """)

        cur.execute("""
            INSERT INTO partners 
                (type_id, name_partner, director, email, tel, adres, inn, rating)
            VALUES
                (1, 'ООО Альфа', 'Иванов И.И.', 'alpha@example.com', '+7 900 111-11-11',
                 'Москва', 7700000001, 5),
                (2, 'ИП Петров', 'Петров П.П.', 'petrov@example.com', '+7 900 222-22-22',
                 'Балашиха', 5000000002, 3);
        """)

if __name__ == "__main__":
    db_create()
    load_data()