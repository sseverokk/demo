import psycopg2

config_admin = {
    'database': "postgres",
    'user': 'postgres',
    'password': '200610',
    'host': 'localhost',
    'port': 5432
}

config = {
    'database': "mydb",
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
    cur.execute("SELECT 1 FROM pg_database WHERE datname='mydb';")
    if not cur.fetchone():
        cur.execute("CREATE DATABASE mydb WITH OWNER admin ENCODING 'UTF8';")
    cur.execute("GRANT ALL PRIVILEGES ON DATABASE mydb TO admin;")
    cur.close()
    con.close()

def load_data():
    with psycopg2.connect(**config) as con:
        cur = con.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS partner_types (
                id   SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS partners (
                id           SERIAL PRIMARY KEY,
                type_id      INT NOT NULL REFERENCES partner_types(id),
                name_partner VARCHAR(255) UNIQUE NOT NULL,
                director     VARCHAR(255),
                email        VARCHAR(255),
                tel          VARCHAR(50),
                adres        TEXT,
                inn          BIGINT,
                rating       NUMERIC(6,2) CHECK (rating >= 0) DEFAULT 0
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id      SERIAL PRIMARY KEY,
                name    VARCHAR(255) NOT NULL,
                article VARCHAR(50) UNIQUE,
                price   NUMERIC(12,2) NOT NULL
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id         SERIAL PRIMARY KEY,
                partner_id INT NOT NULL REFERENCES partners(id) ON DELETE CASCADE,
                sale_date  DATE NOT NULL DEFAULT CURRENT_DATE
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS sale_items (
                id         SERIAL PRIMARY KEY,
                sale_id    INT NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
                product_id INT NOT NULL REFERENCES products(id),
                quantity   NUMERIC(12,2) NOT NULL CHECK (quantity > 0)
            );
        """)

        cur.execute("""
            INSERT INTO partner_types (name)
            VALUES ('Оптовый'), ('Розничный'), ('Онлайн')
            ON CONFLICT (name) DO NOTHING;
        """)

        cur.execute("""
            INSERT INTO partners
                (type_id, name_partner, director, email, tel, adres, inn, rating)
            VALUES
                (1, 'ООО Альфа', 'Иванов И.И.', 'alpha@example.com', '+7 900 111-11-11',
                 'Москва, Ленина 10', 7700000001, 5),
                (2, 'ИП Петров', 'Петров П.П.', 'petrov@example.com', '+7 900 222-22-22',
                 'Балашиха, Парковая 5', 5000000002, 3)
            ON CONFLICT (name_partner) DO NOTHING;
        """)

        cur.execute("""
            INSERT INTO products (name, article, price)
            VALUES
                ('Стол офисный S-120', 'S-120', 7000),
                ('Тумба приставная T-40', 'T-40', 3500),
                ('Шкаф офисный SH-180', 'SH-180', 12000)
            ON CONFLICT (article) DO NOTHING;
        """)

if __name__ == "__main__":
    db_create()
    load_data()