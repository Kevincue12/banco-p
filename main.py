from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import models
from database import SessionLocal, engine, Base

from crud.usuarios import crear_usuario
from crud.bancos import crear_banco, limpiar_inventario
from crud.donaciones import registrar_donacion

from schemas import UsuarioCreate, BancoCreate, DonacionCreate


# Crear tablas en la BD
Base.metadata.create_all(bind=engine)
models.Base.metadata.create_all(bind=engine)


# Crear aplicación FastAPI
app = FastAPI(title="Banco de Alimentos")


# ---------------------------
# SERVIR ARCHIVOS ESTÁTICOS
# ---------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")


# ---------------------------
# SERVIR ARCHIVOS HTML
# ---------------------------
templates = Jinja2Templates(directory="frontend")


# ---------------------------
# DEPENDENCIA DB
# ---------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------
# ENDPOINTS API
# ---------------------------

@app.post("/usuarios/")
def crear_usuario_endpoint(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    return crear_usuario(db, usuario)


@app.post("/bancos/")
def crear_banco_endpoint(banco: BancoCreate, db: Session = Depends(get_db)):
    return crear_banco(db, banco)


@app.post("/donar/")
def registrar_donacion_endpoint(donacion: DonacionCreate, db: Session = Depends(get_db)):
    resultado = registrar_donacion(db, donacion)
    if not resultado:
        return {"mensaje": "No hay bancos disponibles para recibir este alimento."}

    don, banco = resultado
    return {
        "mensaje": "Donación registrada",
        "banco_asignado": banco.nombre,
        "direccion": banco.direccion
    }


@app.delete("/bancos/{banco_id}/limpiar")
def limpiar(banco_id: int, db: Session = Depends(get_db)):
    limpiar_inventario(db, banco_id)
    return {"mensaje": "Inventario limpiado correctamente"}


# ---------------------------
# PAGINA PRINCIPAL (INDEX)
# ---------------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
