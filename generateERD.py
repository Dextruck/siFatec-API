# -*- coding: utf-8 -*-

from sqlalchemy_schemadisplay import create_schema_graph
from sqlalchemy import create_engine
from app.models import Base  # Ajuste conforme o nome do seu pacote
from app.database import SQLALCHEMY_DATABASE_URL  # ou onde estiver sua string de conexão

# Crie a engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Crie o grafo do diagrama
graph = create_schema_graph(
    metadata=Base.metadata,
    engine=engine,
    show_datatypes=True,
    show_indexes=True,
    rankdir='LR',
    concentrate=False
)

# Salve o diagrama
graph.write_png('erd_diagram.png')
