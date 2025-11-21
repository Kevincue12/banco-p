from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL convertida al formato correcto
DATABASE_URL = "postgresql://ujkrbxwszomq7zktmlvk:0OyZZGFZqgPCGBjongZmjPOWIO4Q2s@bxkx37ek1k8qveeaer4f-postgresql.services.clever-cloud.com:5432/bxkx37ek1k8qveeaer4f"

# Crear el motor de conexión
engine = create_engine(DATABASE_URL)

# Crear sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()
