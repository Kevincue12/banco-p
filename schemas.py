from pydantic import BaseModel

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
    alimento: str
    cantidad: int

class DonacionCreate(DonacionBase):
    usuario_id: int
