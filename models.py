from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    correo = Column(String, unique=True)
    tipo_usuario = Column(String)  # "donante" o "propietario"

class Banco(Base):
    __tablename__ = "bancos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    direccion = Column(String)
    capacidad_total = Column(Integer)

class Inventario(Base):
    __tablename__ = "inventario"

    id = Column(Integer, primary_key=True, index=True)
    banco_id = Column(Integer, ForeignKey("bancos.id"))
    alimento = Column(String)
    cantidad = Column(Integer)

class Donacion(Base):
    __tablename__ = "donaciones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    alimento = Column(String)
    cantidad = Column(Integer)
    banco_asignado = Column(Integer, ForeignKey("bancos.id"))
