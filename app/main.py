from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .db import get_db

from . import actions, models, schemas
from .database import SessionLocal, engine
from .auth import authenticate_user, create_access_token, get_home_profile

# Cria as tabelas no banco de dados
models.Base.metadata.create_all(bind=engine)

# Inicializa a aplicação FastAPI
app = FastAPI()

# Rota para criar um usuário
@app.post("/users/", response_model=schemas.Users)
def create_user(users: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = actions.get_user_by_email(db, email=users.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return actions.create_user(db=db, user=users)

# Rota para listar usuários
@app.get("/users/", response_model=list[schemas.Users])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = actions.get_users(db, skip=skip, limit=limit)
    return users

# Rota para obter um usuário específico pelo ID
@app.get("/users/{user_id}", response_model=schemas.Users)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = actions.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Rota de login e criação de token
@app.post("/token", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.user.id), "email":user.user.email, "role":user.role_id})
    return {"access_token": access_token, "token_type": "bearer"}

# Rota para buscar infos da tela inicial
@app.get("/profile", response_model= schemas.UserProfile)
async def home_profile(current_user: models.User = Depends(get_home_profile)):
    return current_user
