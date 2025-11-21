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
    bancos = db.query(models.Banco).all()

    for banco in bancos:
        categorias = banco.categorias or {}
        if donacion.tipo in categorias:
            capacidad = categorias[donacion.tipo].get("capacidad", 0)
            usado = categorias[donacion.tipo].get("usado", 0)
            disponible = capacidad - usado

            if disponible >= donacion.cantidad:
                # Crear donación
                nueva_donacion = models.Donacion(
                    nombre=donacion.nombre,
                    tipo=donacion.tipo,
                    cantidad=donacion.cantidad,
                    banco_id=banco.id
                )
                db.add(nueva_donacion)
                db.commit()
                db.refresh(nueva_donacion)

                # Actualizar inventario (mutable: detecta la mutación)
                categorias[donacion.tipo]["usado"] = usado + donacion.cantidad
                db.add(banco)
                db.commit()
                db.refresh(banco)

                return {
                    "mensaje": f"Donación registrada en {banco.nombre}",
                    "categoria": donacion.tipo,
                    "direccion": banco.direccion,
                    "espacio_usado": banco.categorias[donacion.tipo]["usado"],
                    "espacio_total": banco.categorias[donacion.tipo]["capacidad"]
                }

    return {"mensaje": "No hay bancos disponibles para esta donación"}


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

@app.post("/donar/opciones/simple")
def opciones_donacion_simple(donacion: DonacionCreate, db: Session = Depends(get_db)):
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


@app.post("/donar/greedy/simple")
def donar_greedy_simple(donacion: DonacionCreate, db: Session = Depends(get_db)):
    bancos = db.query(models.Banco).all()
    mejor_banco = None
    mejor_disponible = -1

    for banco in bancos:
        categorias = dict(banco.categorias)
        if donacion.tipo not in categorias:
            continue
        capacidad = categorias[donacion.tipo]["capacidad"]
        usado = categorias[donacion.tipo]["usado"]
        disponible = capacidad - usado

        if disponible >= donacion.cantidad and disponible > mejor_disponible:
            mejor_disponible = disponible
            mejor_banco = banco

    if mejor_banco:
        return {
            "mensaje": "Donación asignada con algoritmo Greedy",
            "banco": mejor_banco.nombre,
            "direccion": mejor_banco.direccion,
            "espacio_disponible": mejor_disponible
        }
    else:
        return {"mensaje": "No hay bancos disponibles para esta donación"}



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
    bancos = db.query(models.Banco).all()

    for banco in bancos:
        categorias = dict(banco.categorias)
        valido = True

        # Verificamos si todas las donaciones caben en este banco
        for item in donacion.donaciones:
            if item.tipo not in categorias:
                valido = False
                break
            capacidad = categorias[item.tipo]["capacidad"]
            usado = categorias[item.tipo].get("usado", 0)  # aseguramos que exista
            disponible = capacidad - usado
            if disponible < item.cantidad:
                valido = False
                break

        if valido:
            # Registrar todas las donaciones en este banco
            for item in donacion.donaciones:
                categorias[item.tipo]["usado"] = categorias[item.tipo].get("usado", 0) + item.cantidad
                nueva = models.Donacion(
                    nombre=donacion.nombre,
                    tipo=item.tipo,
                    cantidad=item.cantidad,
                    banco_id=banco.id
                )
                db.add(nueva)

            # Actualizamos el banco con las nuevas categorías
            banco.categorias = categorias
            db.add(banco)
            db.commit()
            db.refresh(banco)

            return {"mensaje": f"Lote de donaciones registrado en {banco.nombre}"}

    return {"mensaje": "No hay bancos disponibles para este lote"}

@app.post("/donar/greedy")
def donar_greedy(lote: LoteDonacion, db: Session = Depends(get_db)):
    bancos = db.query(models.Banco).all()
    if not bancos:
        return {"mensaje": "No hay bancos disponibles", "resultados": []}

    resultados = []
    for item in lote.donaciones:
        mejor_banco = None
        mejor_disponible = -1

        # Buscar el banco con mayor espacio disponible para este tipo
        for banco in bancos:
            categorias = dict(banco.categorias)
            if item.tipo not in categorias:
                continue
            capacidad = categorias[item.tipo]["capacidad"]
            usado = categorias[item.tipo].get("usado", 0)
            disponible = capacidad - usado

            if disponible >= item.cantidad and disponible > mejor_disponible:
                mejor_disponible = disponible
                mejor_banco = banco

        if mejor_banco:
            categorias = dict(mejor_banco.categorias)
            categorias[item.tipo]["usado"] = categorias[item.tipo].get("usado", 0) + item.cantidad
            mejor_banco.categorias = categorias

            nueva = models.Donacion(
                nombre=lote.nombre,
                tipo=item.tipo,
                cantidad=item.cantidad,
                banco_id=mejor_banco.id
            )
            db.add(nueva)
            db.add(mejor_banco)

            resultados.append({
                "tipo": item.tipo,
                "cantidad": item.cantidad,
                "banco": mejor_banco.nombre,
                "direccion": mejor_banco.direccion,
                "espacio_usado": categorias[item.tipo]["usado"],
                "espacio_total": categorias[item.tipo]["capacidad"]
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
def donar_greedy_opciones(lote: LoteDonacion, db: Session = Depends(get_db)):
    bancos = db.query(models.Banco).all()
    if not bancos:
        return {"mensaje": "No hay bancos disponibles", "opciones": []}

    opciones = []
    for item in lote.donaciones:
        mejor_banco = None
        mejor_disponible = -1

        # Buscar el banco con mayor espacio disponible para este tipo
        for banco in bancos:
            categorias = dict(banco.categorias)
            if item.tipo not in categorias:
                continue
            capacidad = categorias[item.tipo]["capacidad"]
            usado = categorias[item.tipo].get("usado", 0)
            disponible = capacidad - usado

            if disponible >= item.cantidad and disponible > mejor_disponible:
                mejor_disponible = disponible
                mejor_banco = banco

        if mejor_banco:
            opciones.append({
                "tipo": item.tipo,
                "cantidad": item.cantidad,
                "banco": mejor_banco.nombre,
                "direccion": mejor_banco.direccion,
                "espacio_usado": mejor_banco.categorias[item.tipo].get("usado", 0),
                "espacio_total": mejor_banco.categorias[item.tipo]["capacidad"]
            })
        else:
            opciones.append({
                "tipo": item.tipo,
                "cantidad": item.cantidad,
                "mensaje": "No hay espacio suficiente"
            })

    return {"mensaje": "Opciones calculadas con algoritmo Greedy", "opciones": opciones}

@app.delete("/bancos/{banco_id}/limpiar")
def limpiar_banco(banco_id: int, db: Session = Depends(get_db)):
    banco = db.query(models.Banco).filter(models.Banco.id == banco_id).first()
    if not banco:
        return {"mensaje": f"No se encontró el banco con id {banco_id}"}

    categorias = dict(banco.categorias)
    for tipo in categorias:
        categorias[tipo]["usado"] = 0
    banco.categorias = categorias

    db.add(banco)
    db.commit()
    db.refresh(banco)

    return {"mensaje": f"Inventario del banco '{banco.nombre}' limpiado correctamente"}


@app.delete("/bancos/eliminar/{banco_id}")
def eliminar_banco(banco_id: int, db: Session = Depends(get_db)):
    banco = db.query(models.Banco).filter(models.Banco.id == banco_id).first()
    if not banco:
        return {"mensaje": f"No se encontró el banco con id {banco_id}"}

    db.delete(banco)
    db.commit()
    return {"mensaje": f"Banco '{banco.nombre}' eliminado correctamente"}


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