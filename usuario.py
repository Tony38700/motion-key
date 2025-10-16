import psycopg2
from argon2 import PasswordHasher
from credenciais_db import DB_PARAMS

class Usuario:
    def __init__(self, id_pessoa=None, senha_hash=None, login=None, is_admin=False):
        self.id_pessoa = id_pessoa
        self.senha_hash = senha_hash
        self.login = login
        self.is_admin = is_admin

    def cadastrar_no_banco(self, dados, DB_PARAMS):
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        ph = PasswordHasher()
        senha_hash = ph.hash(dados['senha'])
        cursor.execute('''
            INSERT INTO usuario (
                id_pessoa,
                login,
                senha_hash,
                is_admin
            ) VALUES (%s, %s, %s, %s)
        ''', (dados['id_pessoa'], dados['login'], senha_hash, dados.get('is_admin', False)))
        conn.commit()
        cursor.close()
        conn.close()

    def atualizar_valor_usuario(self, id_usuario, novo_valor, coluna, DB_PARAMS):
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        cursor.execute(f'''
            UPDATE usuario
            SET {coluna} = %s
            WHERE id_pessoa = %s;
        ''', (novo_valor, id_usuario))
        conn.commit()
        cursor.close()
        conn.close()

    def pesquisar_no_banco(self, termo, coluna, DB_PARAMS):
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        if termo == '%':
            cursor.execute(f'''
                SELECT * FROM usuario
            ''')
        else:
            cursor.execute(f'''
                SELECT * FROM usuario WHERE usuario.{coluna} = %s
            ''', (termo,))
        resultado_busca = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultado_busca
