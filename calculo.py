import psycopg2

class Calculo:
    def cadastrar_no_banco(self, dados, DB_PARAMS):
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO calculos (
                data_hora_calculo,
                tipo_operacao,
                entrada_dados,
                saida_dados,
                resultado,
                observacoes
            ) VALUES (%s, %s, %s, %s, %s);
        ''',
            (
                dados["data_hora_calculo"],
                dados["tipo_operacao"],
                dados["entrada_dados"],
                dados["saida_dados"],
                dados["resultado"],
                dados["observacoes"]
            )
        )
        conn.commit()
        cursor.close()
        conn.close()

    def pesquisar_no_banco(self, termo, coluna, DB_PARAMS):
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        if termo == '%':
            cursor.execute(f'''
                SELECT * FROM calculos
            ''')
        else:
            cursor.execute(f'''
                SELECT * FROM calculos WHERE calculos.{coluna} = %s
            ''', (termo,))
        resultado_busca = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultado_busca

    def deletar_usuario(self, id_usuario, DB_PARAMS):
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        cursor.execute(
            '''DELETE FROM calculos WHERE id = %s''',
            (id_usuario,))
        conn.commit()
        cursor.close()
        conn.close()
