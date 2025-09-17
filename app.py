import psycopg2
from pessoa import Pessoa
from usuario import Usuario
from credenciais_db import DB_PARAMS
from os import system
from datetime import datetime, timedelta
from argon2 import PasswordHasher, exceptions
ph = PasswordHasher()

def cadastrar_primeiro_usuario():
    print("⚙️ Nenhum usuário encontrado. Vamos cadastrar o primeiro usuário do sistema.\n")

    nome = input("Nome completo: ")
    data_nascimento = input("Data de nascimento (YYYY-MM-DD): ")
    cpf = input("CPF (somente números): ")
    telefone = input("Telefone (somente números): ")
    endereco = input("Endereço: ")
    email = input("Email (opcional): ")

    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    # Inserir pessoa
    cursor.execute("""
        INSERT INTO pessoa (nome_completo, data_nascimento, cpf, telefone, endereco, email)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
    """, (nome, data_nascimento, cpf, telefone, endereco, email))
    id_pessoa = cursor.fetchone()[0]

    # Criar usuário
    login = input("Login: ")
    senha = input("Senha: ")
    senha_hash = ph.hash(senha)

    cursor.execute("""
        INSERT INTO usuario (id_pessoa, login, senha_hash)
        VALUES (%s, %s, %s)
    """, (id_pessoa, login, senha_hash))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Primeiro usuário cadastrado com sucesso!\n")

def cadastrar_usuario():
    print("⚙️ Cadastro de novo usuário\n")

    # Primeiro, cadastrar a pessoa
    nome = input("Nome completo: ")
    data_nascimento = input("Data de nascimento (YYYY-MM-DD): ")
    cpf = input("CPF (somente números): ")
    telefone = input("Telefone (somente números): ")
    endereco = input("Endereço: ")
    email = input("Email (opcional): ")

    with psycopg2.connect(**DB_PARAMS) as conn:
        with conn.cursor() as cursor:
            # Inserir pessoa
            cursor.execute("""
                INSERT INTO pessoa (nome_completo, data_nascimento, cpf, telefone, endereco, email)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
            """, (nome, data_nascimento, cpf, telefone, endereco, email))
            id_pessoa = cursor.fetchone()[0]

            # Solicitar login e senha para o usuário
            login = input("Login do usuário: ")
            senha = input("Senha do usuário: ")
            senha_hash = ph.hash(senha)

            # Inserir usuário com status ativo
            cursor.execute("""
                INSERT INTO usuario (id_pessoa, login, senha_hash)
                VALUES (%s, %s, %s)
            """, (id_pessoa, login, senha_hash))

        conn.commit()

    print("✅ Usuário cadastrado com sucesso!\n")

def deletar_usuario(login_ou_id):
    """
    Deleta um usuário e a pessoa vinculada a ele.
    Pode passar o login ou o id_pessoa.
    """
    with psycopg2.connect(**DB_PARAMS) as conn:
        with conn.cursor() as cursor:
            # Descobrir o id da pessoa
            if isinstance(login_ou_id, int):
                id_pessoa = login_ou_id
            else:
                cursor.execute("SELECT id_pessoa FROM usuario WHERE login = %s", (login_ou_id,))
                row = cursor.fetchone()
                if not row:
                    print("Usuário não encontrado.")
                    return
                id_pessoa = row[0]

            # Deletar a pessoa (o usuário será removido automaticamente)
            cursor.execute("DELETE FROM pessoa WHERE id = %s", (id_pessoa,))
        
        conn.commit()
    print(f"✅ Usuário (id_pessoa={id_pessoa}) e pessoa vinculada deletados com sucesso.")


def validar_entrada(texto, obrigatorio, validacao, erro):
    while True:
        entrada = input(texto)

        if entrada == '-1':
            return entrada
        elif obrigatorio and not entrada:
            print('Campo obrigatorio\n')
            continue
        elif validacao and not validacao(entrada):
            print(erro + '\n')
            continue

        return entrada

def checar_apenas_letras(entrada):
    return entrada.replace(' ', '').isalpha()

def checar_apenas_numeros(entrada):
    return entrada.isdigit()




def main():
    while True:
        # Verificar se já existe algum usuário
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()

        # Verificar se já existe algum usuário
        cursor.execute("SELECT COUNT(*) FROM usuario")
        qtd_usuarios = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        if qtd_usuarios == 0:
            cadastrar_primeiro_usuario()
        
        print('1- Entrar')
        print('2- Sair')
        escolha_inicial = input('>')

        if escolha_inicial == '2':
            break
        elif escolha_inicial != '1':
            continue

        login = input('Login: ')
        senha = input('Senha: ')

        # Conexão segura com with
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT senha_hash FROM usuario WHERE login = %s', (login,))
                row = cursor.fetchone()

        if not row:
            print('Login ou senha incorretos\n')
            continue

        senha_hash = row[0]

        try:
            ph.verify(senha_hash, senha)
            print("✅ Login realizado com sucesso!\n")
        except exceptions.VerifyMismatchError:
            print('Login ou senha incorretos\n')
            continue

        # Menu principal (só aparece depois de login válido)
        while True:
            print('1- Cadastrar usuario')
            print('2- Adicionar gesto')
            print('3- Reorganizar relação gesto/comando')
            print('4- Deletar usuario')
            print('5- Sair')
            escolha_principal = input('>')

            if escolha_principal not in ['1', '2', '3', '4', '5']:
                continue
            elif escolha_principal == '5':
                system('cls')  # limpa tela (Windows)
                break
            elif escolha_principal == '1':
                cadastrar_usuario()
            elif escolha_principal == '2':
                print('Adicionar gesto - Em desenvolvimento\n')
            elif escolha_principal == '3':
                print('Reorganizar relação gesto/comando - Em desenvolvimento\n')
            elif escolha_principal == '4':
                login = input("Digite o login do usuário que deseja deletar: ")
                deletar_usuario(login)
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Erro detectado:", e)

