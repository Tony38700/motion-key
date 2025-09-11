<<<<<<< HEAD
import psycopg2

class Pessoa:
    def __init__(self, id=None, nome=None, data_nascimento=None, cpf=None, telefone=None, 
                 endereco=None, categoria=None, email=None,
                 departamento=None, status=None, data_cadastro=None):
        self.id = id
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf
        self.telefone = telefone
        self.endereco = endereco
        self.categoria = categoria
        self.email = email
        self.status = status
        self.data_cadastro = data_cadastro

    def cadastrar_no_banco(self, dados, DB_PARAMS):
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO pessoa (
                nome_completo,
                data_nascimento,
                cpf,
                telefone,
                endereco,
                email,
                departamento
            ) VALUES (%s, %s, %s, %s, %s, %s, %s);
        ''', (dados["nome_completo"],
              dados["data_nascimento"],
              dados["cpf"],
              dados["telefone"],
              dados["endereco"],
              dados["email"],
              dados["departamento"]))
        conn.commit()
        cursor.close()
        conn.close()

    def pesquisar_no_banco(self, termo, coluna, DB_PARAMS):
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT * FROM Pessoa WHERE Pessoa.{coluna} = %s
        ''', (termo,))
        resultado_busca = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultado_busca

    def atualizar_valor_usuario(self, id_usuario, novo_valor, coluna, DB_PARAMS):
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        cursor.execute(f'''
            UPDATE Pessoa
            SET {coluna} = %s
            WHERE id = %s;
        ''', (novo_valor, id_usuario))
        conn.commit()
        cursor.close()
        conn.close()

    def inativar_usuario(self, id_usuario, DB_PARAMS):
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE Usuario
            SET status = 'inativo'
            WHERE id_pessoa = %s;
        ''', (id_usuario,))
        conn.commit()
        cursor.close()
        conn.close()
=======
import psycopg2

class Pessoa:
    def __init__(self, id=None, nome=None, data_nascimento=None, cpf=None, telefone=None, 
                 endereco=None, categoria=None, email=None,
                 departamento=None, status=None, data_cadastro=None):
        self.id = id
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf
        self.telefone = telefone
        self.endereco = endereco
        self.categoria = categoria
        self.email = email
        self.status = status
        self.data_cadastro = data_cadastro

    def cadastrar_no_banco(self, dados, DB_PARAMS):
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO pessoa (
                nome_completo,
                data_nascimento,
                cpf,
                telefone,
                endereco,
                email,
                departamento
            ) VALUES (%s, %s, %s, %s, %s, %s, %s);
        ''', (dados["nome_completo"],
              dados["data_nascimento"],
              dados["cpf"],
              dados["telefone"],
              dados["endereco"],
              dados["email"],
              dados["departamento"]))
        conn.commit()
        cursor.close()
        conn.close()

    def pesquisar_no_banco(self, termo, coluna, DB_PARAMS):
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT * FROM Pessoa WHERE Pessoa.{coluna} = %s
        ''', (termo,))
        resultado_busca = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultado_busca

    def atualizar_valor_usuario(self, id_usuario, novo_valor, coluna, DB_PARAMS):
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        cursor.execute(f'''
            UPDATE Pessoa
            SET {coluna} = %s
            WHERE id = %s;
        ''', (novo_valor, id_usuario))
        conn.commit()
        cursor.close()
        conn.close()

    def inativar_usuario(self, id_usuario, DB_PARAMS):
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE Usuario
            SET status = 'inativo'
            WHERE id_pessoa = %s;
        ''', (id_usuario,))
        conn.commit()
        cursor.close()
        conn.close()
>>>>>>> 2cda65454b640299702893de01a475eb01697e5c
