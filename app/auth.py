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
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    if not verify_password(password, user.password):
        return False
    
    user_roles = [role.role_id for role in user.roles] 
    authenticated_user = schemas.AuthenticatedUser(user=user.__dict__, role_id=user_roles)

    return authenticated_user



def create_access_token(data: dict):
    to_encode = data.copy()
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user(db: Session, email: str):
    return actions.get_user_by_email(db, email)


# Valida o token enviado pelo usuário e retorna as iformações de identificação
async def token_info_validate(token: str = Depends(oauth2_scheme)):

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

    return payload



# Retorna o profile do usuário logado
async def get_home_profile(db: Session = Depends(get_db), token: dict = Depends(token_info_validate)):
    user_id = int(token.get("sub"))
    user = actions.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    period = max([sp.course_period for sp in user.student_periods], default=0) if user.student_periods else 0
    
    if not user.profile:
        raise HTTPException(status_code=500, detail="Perfil do usuário não encontrado")
    
    # Calcular percentual de progresso
    progress_percentage = 0.0
    average_grade = 0.0
    
    # Buscar o curso atual do aluno (última matrícula ativa)
    current_enrollment = db.query(models.Enrollment).join(models.EnrollmentsStatus)\
        .filter(models.Enrollment.student_id == user_id)\
        .filter(models.EnrollmentsStatus.status.in_(["Ativo", "Cursando"]))\
        .order_by(models.Enrollment.created_at.desc())\
        .first()
    
    if current_enrollment and current_enrollment.course:
        # Assumindo que cada ano = 2 períodos (semestres)
        total_periods = current_enrollment.course.duration_years * 2
        if total_periods > 0:
            progress_percentage = min((period / total_periods) * 100, 100.0)
    
    # Calcular média de rendimento
    if current_enrollment:
        # Buscar todas as notas do aluno
        scores_query = db.query(models.Score)\
            .join(models.AssessmentInstrument)\
            .join(models.ClassGroup)\
            .filter(models.Score.enrollment_id == current_enrollment.id)\
            .all()
        
        if scores_query:
            # Calcular média ponderada considerando os pesos dos instrumentos
            total_weighted_score = 0
            total_weight = 0
            
            for score in scores_query:
                weight = score.assessment_instrument.weight or 1  # peso padrão 1 se não definido
                total_weighted_score += score.value * weight
                total_weight += weight
            
            if total_weight > 0:
                average_grade = total_weighted_score / total_weight
    
    user_profile = schemas.UserProfile(
        name=user.full_name,
        registration_number=user.profile.registration_number,
        student_period=period,
        progress_percentage=round(progress_percentage, 2),
        average_grade=round(average_grade, 2)
    )
    
    return user_profile