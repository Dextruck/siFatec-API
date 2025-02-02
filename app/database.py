from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# String de conexão para o PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://fastapi_test:fastapi_test_password@localhost/fastapi_test_db"

# Cria o engine do SQLAlchemy
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Cria uma sessão local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()