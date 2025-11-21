from pydantic import BaseModel
from typing import List

class UsuarioBase(BaseModel):
    nombre: str
    correo: str
    tipo_usuario: str

class UsuarioCreate(UsuarioBase):
    pass

class Usuario(UsuarioBase):
    id: int
    class Config:
        orm_mode = True


class BancoBase(BaseModel):
    nombre: str
    direccion: str
    capacidad_total: int

class BancoCreate(BancoBase):
    pass


class DonacionBase(BaseModel):
    nombre: str          # nombre del donante o referencia
    cantidad: int
    tipo: str            # frutas, granos, enlatados

class DonacionCreate(DonacionBase):
    pass   # ❌ ya no pedimos banco_id


class DonacionItem(BaseModel):
    tipo: str
    cantidad: int

class LoteDonacion(BaseModel):
    nombre: str
    donaciones: List[DonacionItem]
    # ❌ eliminamos banco_id, el sistema asigna el banco automáticamente