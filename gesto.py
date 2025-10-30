import psycopg2

class Gesto:
    def cadastrar_no_banco(self, dados, DB_PARAMS):
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO gestos (
                data_hora_gesto,
                dedos,
                nome_gesto,
                confianca,
                posicao_mao,
                id_usuario,
                mao_usada
            ) VALUES (%s, %s, %s, %s, %s, %s, %s);
        ''',
            (
                dados["data_hora_gesto"],
                dados["dedos"],
                dados["nome_gesto"],
                dados["confianca"],
                dados["posicao_mao"],
                dados.get("id_usuario"),
                dados.get("mao_usada")
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
                SELECT * FROM gestos
            ''')
        else:
            cursor.execute(f'''
                SELECT * FROM gestos WHERE gestos.{coluna} = %s
            ''', (termo,))
        resultado_busca = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultado_busca

    def deletar_usuario(self, id_usuario, DB_PARAMS):
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        cursor.execute(
            '''DELETE FROM gestos WHERE id = %s''',
            (id_usuario,))
        conn.commit()
        cursor.close()
        conn.close()
