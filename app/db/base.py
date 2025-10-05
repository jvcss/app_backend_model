from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Importa os modelos para que sejam registrados com a Base
from app.models import user, team, password_reset

