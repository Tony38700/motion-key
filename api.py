import subprocess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Permite que o front em localhost acesse a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class User(BaseModel):
    id: int
    name: str
    login: str
    password: str
    cpf: str
    birth: Optional[str] = ""
    phone: Optional[str] = ""
    address: Optional[str] = ""
    email: Optional[str] = ""
    is_admin: bool = False

class UserCreate(BaseModel):
    name: str
    login: str
    password: str
    cpf: str
    birth: Optional[str] = ""
    phone: Optional[str] = ""
    address: Optional[str] = ""
    email: Optional[str] = ""
    is_admin: bool = False

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

# DB (simulação em memória)
users: List[User] = []
current_id = 1

@app.post("/register", response_model=User)
def register_user(new_user: UserCreate):
    global current_id

    if any(u.login == new_user.login for u in users):
        raise HTTPException(status_code=400, detail="Login já existe")
    if any(u.cpf == new_user.cpf for u in users):
        raise HTTPException(status_code=400, detail="CPF já cadastrado")

    user = User(
        id=current_id,
        name=new_user.name,
        login=new_user.login,
        password=new_user.password,
        cpf=new_user.cpf,
        birth=new_user.birth,
        phone=new_user.phone,
        address=new_user.address,
        email=new_user.email,
        is_admin=new_user.is_admin,
    )
    users.append(user)
    current_id += 1
    return user

@app.post("/self-register", response_model=User)
def self_register_user(new_user: UserSelfRegister):
    global current_id

    if any(u.login == new_user.login for u in users):
        raise HTTPException(status_code=400, detail="Login já existe")
    if any(u.cpf == new_user.cpf for u in users):
        raise HTTPException(status_code=400, detail="CPF já cadastrado")

    # Valida código de admin
    is_admin = False
    if new_user.admin_code:
        if new_user.admin_code != "123456":
            raise HTTPException(status_code=400, detail="Código de administrador inválido")
        is_admin = True

    user = User(
        id=current_id,
        name=new_user.name,
        birth=new_user.birth,
        cpf=new_user.cpf,
        phone=new_user.phone,
        address=new_user.address,
        email=new_user.email,
        login=new_user.login,
        password=new_user.password,
        is_admin=is_admin,
    )
    users.append(user)
    current_id += 1
    return user

@app.post("/login", response_model=User)
def login_user(credentials: UserLogin):
    for u in users:
        if u.login == credentials.login and u.password == credentials.password:
            return u
    raise HTTPException(status_code=401, detail="Login ou senha inválidos")

@app.get("/users", response_model=List[User])
def list_users():
    return users

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    for u in users:
        if u.id == user_id:
            return u
    raise HTTPException(status_code=404, detail="Usuário não encontrado")

@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, update: UserUpdate):
    for u in users:
        if u.id == user_id:
            u.name = update.name
            u.birth = update.birth
            u.phone = update.phone
            u.address = update.address
            u.email = update.email
            u.password = update.password
            return u
    raise HTTPException(status_code=404, detail="Usuário não encontrado")

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    global users
    for u in users:
        if u.id == user_id:
            users = [usr for usr in users if usr.id != user_id]
            return {"detail": f"Usuário {u.name} removido"}
    raise HTTPException(status_code=404, detail="Usuário não encontrado")

@app.post("/run-motionkey")
def run_motionkey():
    try:
        result = subprocess.run(
            ["python", "maouse.py"],  # ou "python3" dependendo do ambiente
            capture_output=True,
            text=True,
            check=True
        )
        return {"detail": "MotionKey executado com sucesso!", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao executar MotionKey: {e.stderr}"
        )
