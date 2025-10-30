import subprocess
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from fastapi.middleware.cors import CORSMiddleware
from pessoa import Pessoa
from usuario import Usuario
from gesto import Gesto
from calculo import Calculo
from credenciais_db import DB_PARAMS
from argon2 import PasswordHasher, exceptions

app = FastAPI()

# Permite que o front em localhost acesse a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ph = PasswordHasher()

class UserSelfRegister(BaseModel):
    name: str
    birth: str
    cpf: str
    phone: str
    address: str
    email: str
    login: str
    password: str
    admin_code: str = ""

class UserLogin(BaseModel):
    login: str
    password: str

class UserUpdate(BaseModel):
    name: str
    birth: str
    phone: str
    address: str
    email: Optional[str] = ""
    password: str
    is_admin: bool = False

class Gesture(BaseModel):
    timestamp: str
    fingers: str
    gesture_name: str
    confidence: float
    hand_position: str
    user_id: Optional[int] = None
    hand_used: Optional[str] = None

class Calculation(BaseModel):
    timestamp: str
    operation_type: str
    input_data: str
    output_data: str
    result: str
    additional_info: str

class RunRequest(BaseModel):
    # expected values: "right" or "left" (default: right)
    hand: str = "right"
    current_user: Optional[dict] = None

@app.post("/self-register")
def self_register_user(new_user: UserSelfRegister):
    pessoa = Pessoa()
    usuario = Usuario()

    if pessoa.pesquisar_no_banco(new_user.cpf, "cpf", DB_PARAMS):
        raise HTTPException(status_code=400, detail="CPF já cadastrado")
    if usuario.pesquisar_no_banco(new_user.login, "login", DB_PARAMS):
        raise HTTPException(status_code=400, detail="Login já existe")

    is_admin = False
    if new_user.admin_code:
        if new_user.admin_code != "123456":
            raise HTTPException(status_code=400, detail="Código de administrador inválido")
        is_admin = True

    dados_pessoa = {
        "nome_completo": new_user.name,
        "data_nascimento": new_user.birth,
        "cpf": new_user.cpf,
        "telefone": new_user.phone,
        "endereco": new_user.address,
        "email": new_user.email,
    }
    pessoa.cadastrar_no_banco(dados_pessoa, DB_PARAMS)
    id_pessoa = pessoa.pesquisar_no_banco(new_user.cpf, "cpf", DB_PARAMS)[0][0]

    dados_usuario = {"id_pessoa": id_pessoa, "login": new_user.login, "senha": new_user.password, "is_admin": is_admin}
    usuario.cadastrar_no_banco(dados_usuario, DB_PARAMS)

    return {"detail": f"Usuário {new_user.login} registrado com sucesso", "id_pessoa": id_pessoa, "is_admin": is_admin}

@app.post("/login")
def login_user(credentials: UserLogin):
    usuario = Usuario()
    pessoa = Pessoa()

    result = usuario.pesquisar_no_banco(credentials.login, "login", DB_PARAMS)
    if not result:
        raise HTTPException(status_code=401, detail="Login ou senha inválidos")

    id_pessoa, login, senha_hash, is_admin = result[0]
    try:
        ph.verify(senha_hash, credentials.password)
    except exceptions.VerifyMismatchError:
        raise HTTPException(status_code=401, detail="Login ou senha inválidos")

    pessoa_data = pessoa.pesquisar_no_banco(id_pessoa, "id", DB_PARAMS)[0]
    return {
        "id_pessoa": pessoa_data[0],
        "name": pessoa_data[1],
        "cpf": pessoa_data[3],
        "phone": pessoa_data[4],
        "address": pessoa_data[5],
        "email": pessoa_data[6],
        "login": login,
        "is_admin": is_admin
    }

@app.get("/users")
def list_users():
    pessoa = Pessoa()
    usuario = Usuario()
    usuarios = []

    results = usuario.pesquisar_no_banco("%", "id_pessoa", DB_PARAMS)  # Busca todos
    for row in results:
        id_pessoa = row[0]
        login = row[1]
        is_admin = row[3]
        pessoa_data = pessoa.pesquisar_no_banco(id_pessoa, "id", DB_PARAMS)[0]
        usuarios.append({
            "id_pessoa": pessoa_data[0],
            "name": pessoa_data[1],
            "cpf": pessoa_data[3],
            "phone": pessoa_data[4],
            "address": pessoa_data[5],
            "email": pessoa_data[6],
            "login": login,
            "is_admin": is_admin
        })
    return usuarios

@app.get("/users/{user_id}")
def get_user(user_id: int):
    pessoa = Pessoa()
    usuario = Usuario()

    result = usuario.pesquisar_no_banco(user_id, "id_pessoa", DB_PARAMS)[0]
    id_pessoa = result[0]
    login = result[1]
    is_admin = result[3]
    pessoa_data = pessoa.pesquisar_no_banco(id_pessoa, "id", DB_PARAMS)[0]
    user = {
        "id_pessoa": pessoa_data[0],
        "name": pessoa_data[1],
        "cpf": pessoa_data[3],
        "phone": pessoa_data[4],
        "address": pessoa_data[5],
        "email": pessoa_data[6],
        "login": login,
        "is_admin": is_admin
    }
    return user

@app.put("/users/{user_id}")
def update_user(user_id: int, update: UserUpdate):
    pessoa = Pessoa()

    pessoa.atualizar_valor_usuario(user_id, update.name, "nome_completo", DB_PARAMS)
    pessoa.atualizar_valor_usuario(user_id, update.birth, "data_nascimento", DB_PARAMS)
    pessoa.atualizar_valor_usuario(user_id, update.phone, "telefone", DB_PARAMS)
    pessoa.atualizar_valor_usuario(user_id, update.address, "endereco", DB_PARAMS)
    pessoa.atualizar_valor_usuario(user_id, update.email, "email", DB_PARAMS)

    if update.password:
        usuario = Usuario()
        senha_hash = ph.hash(update.password)
        usuario.atualizar_valor_usuario(user_id, senha_hash, "senha_hash", DB_PARAMS)

    return {"detail": f"Usuário id={user_id} atualizado com sucesso"}

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    pessoa = Pessoa()
    pessoa.deletar_usuario(user_id, DB_PARAMS)
    return {"detail": f"Usuário id={user_id} inativado com sucesso"}

@app.post("/run-motionkey")
def run_motionkey(req: RunRequest):
    hand = (req.hand or "right").lower()
    if hand not in ("right", "left"):
        raise HTTPException(status_code=400, detail="Parâmetro 'hand' inválido. Use 'right' ou 'left'.")

    script = "maouse.py" if hand == "right" else "maouse_esq.py"

    try:
        # Use the same Python interpreter that's running the API to avoid "python" vs "python3" issues
        env = os.environ.copy()
        if req.current_user and isinstance(req.current_user, dict):
            try:
                uid = req.current_user.get('id_pessoa')
                if uid is not None:
                    env['USER_ID'] = str(uid)
            except Exception:
                pass

        result = subprocess.run(
            [sys.executable, script],
            capture_output=True,
            text=True,
            check=True,
            env=env,
        )
        return {"detail": f"MotionKey ({hand}) executado com sucesso!", "output": result.stdout}
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"Script '{script}' não encontrado no servidor.")
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao executar MotionKey ({hand}): {e.stderr or e.stdout}"
        )

@app.post('/gesture')
def register_gesture(gesture: Gesture):
    gesto = Gesto()

    hand_used_value = None
    if gesture.hand_used:
        hw = gesture.hand_used.lower()
        if hw in ('right', 'direita'):
            hand_used_value = 'direita'
        elif hw in ('left', 'esquerda'):
            hand_used_value = 'esquerda'

    # Use client-provided user_id (English key) mapped to Portuguese DB column id_usuario
    user_id_value = gesture.user_id if getattr(gesture, 'user_id', None) is not None else None

    dados = {
        'data_hora_gesto': gesture.timestamp,
        'dedos': gesture.fingers,
        'nome_gesto': gesture.gesture_name,
        'confianca': gesture.confidence,
        'posicao_mao': gesture.hand_position,
        'id_usuario': user_id_value,
        'mao_usada': hand_used_value
    }

    gesto.cadastrar_no_banco(dados, DB_PARAMS)

@app.post('/calculation')
def register_calculation(calculation: Calculation):
    calculo = Calculo()

    dados = {
        'data_hora_calculo': calculation.timestamp,
        'tipo_operacao': calculation.operation_type,
        'entrada_dados': calculation.input_data,
        'saida_dados': calculation.output_data,
        'resultado':calculation.result,
        'observacoes':calculation.additional_info
    }

    calculo.cadastrar_no_banco(dados, DB_PARAMS)

@app.get('/gesture')
def get_gesture():
    gesto = Gesto()
    resultado = gesto.pesquisar_no_banco('%', '', DB_PARAMS)
    return resultado

@app.get('/calculation')
def get_calculation():
    calculo = Calculo()
    resultado = calculo.pesquisar_no_banco('%', '', DB_PARAMS)
    return resultado
