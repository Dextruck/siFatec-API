from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import models, schemas, actions
from .db import get_db
from .database import SessionLocal

# Chave secreta para codificação do JWT
SECRET_KEY = "secreta-aqui-mas-use-uma-forte-em-producao"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Instância do gerador de hash
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Funções auxiliares

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Chamada no envio do login para validar o user e retornar infos uteis para o token
def authenticate_user(db: Session, email: str, password: str):
    user = actions.get_user_by_email(db, email)
    if not user or not verify_password(password, user.password):
        return False
    user_roles = [role.role_id for role in user.roles] 
    authenticated_user = schemas.AuthenticatedUser(user=user.__dict__, role_id=user_roles)
    return authenticated_user

def create_access_token(data: dict):
    to_encode = data.copy()
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user(db: Session, email: str):
    return actions.get_user_by_email(db, email)

# Retorna o profile do usuário logado
# Ainda não está finalizada. Falta trazer percenntual de progressão e rendimento
async def get_home_profile(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception

    user = actions.get_user(db, user_id)
    if user is None:
        raise credentials_exception
    
    period = max([sp.course_period for sp in user.student_periods], default=0) if user.student_periods else 0

    if not user.profile:
        raise HTTPException(status_code=500, detail="Perfil do usuário não encontrado")
    
    user_profile = schemas.UserProfile(
        name=user.full_name, 
        registration_number=user.profile.registration_number, 
        student_period=period
    )

    return user_profile