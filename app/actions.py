from sqlalchemy.orm import Session


from . import models, schemas
from .auth import hash_password




def get_user(db: Session, user_id: int):
  return db.query(models.User).filter(models.User.id == user_id).first()


def get_role_by_id(db: Session, user_id: int):
  return db.query(models.UsersRoles).filter(models.UsersRoles.user_id == user_id).first()

def get_user_by_email(db: Session, email: str):
  return db.query(models.User).filter(models.User.email == email).first()




def get_users(db: Session, skip: int = 0, limit: int = 100):
  return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
  hashed_password = hash_password(user.password)
  db_user = models.User(
    name=user.name,
    username=user.username,
    full_name=user.full_name,
    email=user.email,
    cpf=user.cpf,
    password=hashed_password,
    is_active=user.is_active
  )
  db.add(db_user)
  db.commit()
  db.refresh(db_user)
  return db_user