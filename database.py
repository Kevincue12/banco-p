from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL convertida al formato correcto
DATABASE_URL = "postgresql+psycopg2://u3iv3oogobm7bmrk10th:Wu2WZKF7UfHlUXb8N1md@bnxncp4yiyknwxikvfo2-postgresql.services.clever-cloud.com:7799/bnxncp4yiyknwxikvfo2"

# Crear el motor de conexión
engine = create_engine(DATABASE_URL)

# Crear sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()
