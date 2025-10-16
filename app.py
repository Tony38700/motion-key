import psycopg
from pessoa import Pessoa
from usuario import Usuario
from credenciais_db import DB_PARAMS
from argon2 import PasswordHasher, exceptions

ph = PasswordHasher()

def inicializar_banco():
    db_name = DB_PARAMS.get("dbname")

    with psycopg.connect(
        host=DB_PARAMS.get("host"),
        dbname="postgres",
        user=DB_PARAMS.get("user"),
        password=DB_PARAMS.get("password"),
        port=DB_PARAMS.get("port")
    ) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            if not cur.fetchone():
                cur.execute(f"CREATE DATABASE {db_name}")
                print(f"✅ Banco de dados '{db_name}' criado com sucesso.")

    with open("create_tables.txt", "r", encoding="utf-8") as f:
        script = f.read()

    with psycopg.connect(**DB_PARAMS) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(script)
    print("✅ Tabelas criadas ou já existentes.\n")
