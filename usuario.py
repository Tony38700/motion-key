import psycopg2
from argon2 import PasswordHasher
from credenciais_db import DB_PARAMS
conn = psycopg2.connect(**DB_PARAMS)
cursor = conn.cursor()

class Usuario:
    def __init__(self, id_pessoa=None,
                status=None, senha=None, login=None):
        self.id_pessoa = id_pessoa
        self.status = status
        self.senha = senha
        self.login = login

    def cadastrar_no_banco(self, dados, DB_PARAMS):
        ph = PasswordHasher()
        senha_hash = ph.hash(dados['senha'])
        cursor.execute('''
            INSERT INTO usuario (
                id_pessoa,
                status,
                login,
                senha_hash
            ) VALUES (%s, 'ativo', %s, %s)
        ''', (dados['id_pessoa'], dados['login'], senha_hash))
        conn.commit()
        cursor.close()
        conn.close()

    def pesquisar_no_banco(self, termo, coluna, DB_PARAMS):
        cursor.execute(f'''
            SELECT * FROM usuario WHERE usuario.{coluna} = %s
        ''', (termo,))
        resultado_busca = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultado_busca
