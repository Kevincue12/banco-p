from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import models
from database import SessionLocal, engine, Base
from crud.usuarios import crear_usuario
from crud.bancos import crear_banco, limpiar_inventario
from crud.donaciones import registrar_donacion
from schemas import UsuarioCreate, BancoCreate, DonacionCreate, LoteDonacion

# Crear tablas
Base.metadata.create_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Banco de Alimentos")

# Montar carpeta static (CSS, JS, HTML)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependencia de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------- API JSON -------------------

@app.post("/usuarios/")
def crear_usuario_endpoint(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    return crear_usuario(db, usuario)

@app.post("/bancos/")
def crear_banco_endpoint(banco: BancoCreate, db: Session = Depends(get_db)):
    crear_banco(db, banco)
    return {"mensaje": "Banco registrado exitosamente"}

@app.post("/donar/")
def registrar_donacion_endpoint(donacion: DonacionCreate, db: Session = Depends(get_db)):
    banco = db.query(models.Banco).filter(models.Banco.id == donacion.banco_id).first()
    if not banco:
        return {"mensaje": "Banco no encontrado"}

    categorias = dict(banco.categorias)
    if donacion.tipo not in categorias:
        return {"mensaje": f"Categoría {donacion.tipo} no válida"}

    if categorias[donacion.tipo]["usado"] + donacion.cantidad > categorias[donacion.tipo]["capacidad"]:
        return {"mensaje": "No hay espacio disponible en esta categoría"}

    categorias[donacion.tipo]["usado"] += donacion.cantidad
    banco.categorias = categorias

    nueva_donacion = models.Donacion(
        nombre=donacion.nombre,
        tipo=donacion.tipo,
        cantidad=donacion.cantidad,
        banco_id=donacion.banco_id
    )
    db.add(nueva_donacion)
    db.commit()
    db.refresh(banco)
    db.refresh(nueva_donacion)

    return {
        "mensaje": f"Donación registrada en {banco.nombre}",
        "categoria": donacion.tipo,
        "direccion": banco.direccion,
        "espacio_usado": banco.categorias[donacion.tipo]["usado"],
        "espacio_total": banco.categorias[donacion.tipo]["capacidad"]
    }

@app.post("/donar/opciones")
def opciones_donacion(donacion: DonacionCreate, db: Session = Depends(get_db)):
    bancos = db.query(models.Banco).all()
    resultados = []

    for banco in bancos:
        categorias = dict(banco.categorias)
        if donacion.tipo not in categorias:
            continue
        capacidad = categorias[donacion.tipo]["capacidad"]
        usado = categorias[donacion.tipo]["usado"]
        disponible = capacidad - usado

        if disponible >= donacion.cantidad:
            resultados.append({
                "id": banco.id,
                "nombre": banco.nombre,
                "direccion": banco.direccion,
                "disponible": disponible
            })

    resultados.sort(key=lambda x: x["disponible"], reverse=True)
    return resultados

@app.post("/donar/opciones/lote")
def opciones_lote(donacion: LoteDonacion, db: Session = Depends(get_db)):
    bancos = db.query(models.Banco).all()
    resultados = []

    for banco in bancos:
        categorias = dict(banco.categorias)
        valido = True
        for item in donacion.donaciones:
            if item.tipo not in categorias:
                valido = False
                break
            capacidad = categorias[item.tipo]["capacidad"]
            usado = categorias[item.tipo]["usado"]
            disponible = capacidad - usado
            if disponible < item.cantidad:
                valido = False
                break
        if valido:
            resultados.append({
                "id": banco.id,
                "nombre": banco.nombre,
                "direccion": banco.direccion
            })

    return resultados

@app.post("/donar/lote")
def registrar_lote(donacion: LoteDonacion, db: Session = Depends(get_db)):
    banco = db.query(models.Banco).filter(models.Banco.id == donacion.banco_id).first()
    if not banco:
        return {"mensaje": "Banco no encontrado"}

    categorias = dict(banco.categorias)
    for item in donacion.donaciones:
        if item.tipo not in categorias:
            return {"mensaje": f"Categoría {item.tipo} no válida"}
        if categorias[item.tipo]["usado"] + item.cantidad > categorias[item.tipo]["capacidad"]:
            return {"mensaje": f"No hay espacio suficiente para {item.tipo}"}

        categorias[item.tipo]["usado"] += item.cantidad
        nueva = models.Donacion(
            nombre=donacion.nombre,
            tipo=item.tipo,
            cantidad=item.cantidad,
            banco_id=donacion.banco_id
        )
        db.add(nueva)

    banco.categorias = categorias
    db.commit()
    db.refresh(banco)

    return {"mensaje": f"Lote de donaciones registrado en {banco.nombre}"}

@app.post("/donar/greedy")
def donar_greedy(lote: LoteDonacion, db: Session = Depends(get_db)):
    bancos = db.query(models.Banco).all()
    if not bancos:
        return {"mensaje": "No hay bancos disponibles", "resultados": []}

    resultados = []
    for item in lote.donaciones:
        mejor_banco = None
        mejor_disponible = -1

        for banco in bancos:
            categorias = dict(banco.categorias)
            if item.tipo not in categorias:
                continue
            capacidad = categorias[item.tipo]["capacidad"]
            usado = categorias[item.tipo]["usado"]
            disponible = capacidad - usado

            if disponible >= item.cantidad and disponible > mejor_disponible:
                mejor_disponible = disponible
                mejor_banco = banco

        if mejor_banco:
            categorias = dict(mejor_banco.categorias)
            categorias[item.tipo]["usado"] += item.cantidad
            mejor_banco.categorias = categorias

            nueva = models.Donacion(
                nombre=lote.nombre,
                tipo=item.tipo,
                cantidad=item.cantidad,
                banco_id=mejor_banco.id
            )
            db.add(nueva)

            resultados.append({
                "tipo": item.tipo,
                "cantidad": item.cantidad,
                "banco": mejor_banco.nombre,
                "direccion": mejor_banco.direccion
            })
        else:
            resultados.append({
                "tipo": item.tipo,
                "cantidad": item.cantidad,
                "mensaje": "No hay espacio suficiente"
            })

    db.commit()
    return {"mensaje": "Donaciones procesadas con algoritmo Greedy", "resultados": resultados}

@app.post("/donar/greedy/opciones")
def greedy_preview(lote: LoteDonacion, db: Session = Depends(get_db)):
    bancos = db.query(models.Banco).all()
    if not bancos:
        return {"mensaje": "No hay bancos disponibles", "resultados": []}

    resultados = []
    for item in lote.donaciones:
        mejor_banco = None
        mejor_disponible = -1
        for banco in bancos:
            categorias = dict(banco.categorias)
            if item.tipo not in categorias:
                continue
            capacidad = categorias[item.tipo]["capacidad"]
            usado = categorias[item.tipo]["usado"]
            disponible = capacidad - usado
            if disponible >= item.cantidad and disponible > mejor_disponible:
                mejor_disponible = disponible
                mejor_banco = banco
        if mejor_banco:
            resultados.append({
                "tipo": item.tipo,
                "cantidad": item.cantidad,
                "banco": mejor_banco.nombre,
                "direccion": mejor_banco.direccion
            })
        else:
            resultados.append({
                "tipo": item.tipo,
                "cantidad": item.cantidad,
                "mensaje": "No hay espacio suficiente"
            })
    return {"mensaje": "Asignación sugerida (Greedy)", "resultados": resultados}

@app.delete("/bancos/{banco_id}/limpiar")
def limpiar(banco_id: int, db: Session = Depends(get_db)):
    banco = limpiar_inventario(db, banco_id)
    if banco:
        return {"mensaje": "Inventario limpiado correctamente"}
    return {"mensaje": "Banco no encontrado"}

@app.get("/api/bancos/listar")
def listar_bancos_endpoint(db: Session = Depends(get_db)):
    bancos = db.query(models.Banco).all()
    return [
        {
            "id": b.id,
            "nombre": b.nombre,
            "direccion": b.direccion,
            "categorias": b.categorias
        }
        for b in bancos
    ]

@app.get("/api/donaciones/listar")
def listar_donaciones_endpoint(db: Session = Depends(get_db)):
    donaciones = db.query(models.Donacion).all()
    return [
        {
            "id": d.id,
            "nombre": d.nombre,
            "tipo": d.tipo,
            "cantidad": d.cantidad,
            "banco_id": d.banco_id
        }
        for d in donaciones
    ]

# ------------------- Páginas HTML -------------------

@app.get("/", response_class=HTMLResponse)
def home():
    return FileResponse("static/index.html")

@app.get("/donar")
def mostrar_donante():
    return FileResponse("static/donante.html")

@app.get("/banco")
def mostrar_banco():
    return FileResponse("static/banco.html")

@app.get("/propietario")
def mostrar_propietario():
    return FileResponse("static/propietario.html")

@app.get("/bancos")
def mostrar_bancos():
    return FileResponse("static/bancos.html")