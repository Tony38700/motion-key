import psycopg2

class Pessoa:
    def __init__(self, id=None, nome=None, data_nascimento=None, cpf=None, telefone=None, 
                 endereco=None, email=None):
        self.id = id
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf
        self.telefone = telefone
        self.endereco = endereco
        self.email = email

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
                email
            ) VALUES (%s, %s, %s, %s, %s, %s);
        ''', (dados["nome_completo"],
              dados["data_nascimento"],
              dados["cpf"],
              dados["telefone"],
              dados["endereco"],
              dados["email"]))
        conn.commit()
        cursor.close()
        conn.close()

    def pesquisar_no_banco(self, termo, coluna, DB_PARAMS):
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        if termo == '%':
            cursor.execute(f'''
                SELECT * FROM pessoa
            ''')
        else:
            cursor.execute(f'''
                SELECT * FROM pessoa WHERE pessoa.{coluna} = %s
            ''', (termo,))
        resultado_busca = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultado_busca

    def atualizar_valor_usuario(self, id_usuario, novo_valor, coluna, DB_PARAMS):
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        cursor.execute(f'''
            UPDATE pessoa
            SET {coluna} = %s
            WHERE id = %s;
        ''', (novo_valor, id_usuario))
        conn.commit()
        cursor.close()
        conn.close()

    def deletar_usuario(self, id_usuario, DB_PARAMS):
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        cursor.execute(
            '''DELETE FROM pessoa WHERE id = %s''',
            (id_usuario,))
        conn.commit()
        cursor.close()
        conn.close()
