from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)
    correo = Column(String, unique=True, index=True, nullable=False)
    contrasena = Column(String, nullable=False)

class Banco(Base):
    __tablename__ = "bancos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)
    direccion = Column(String, index=True, nullable=False)
    capacidad_total = Column(Integer, nullable=False)

    # 👉 Guardamos las categorías como JSONB
    categorias = Column(JSONB, nullable=False)

    # Relación con donaciones
    donaciones = relationship("Donacion", back_populates="banco")

class Donacion(Base):
    __tablename__ = "donaciones"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)
    tipo = Column(String, index=True, nullable=False)   # frutas, granos, enlatados
    cantidad = Column(Integer, nullable=False)

    # Relación con banco
    banco_id = Column(Integer, ForeignKey("bancos.id"), nullable=False)
    banco = relationship("Banco", back_populates="donaciones")