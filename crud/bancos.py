from models import Banco, Inventario

def crear_banco(db, banco):
    nuevo = Banco(
        nombre=banco.nombre,
        direccion=banco.direccion,
        capacidad_total=banco.capacidad_total
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

def limpiar_inventario(db, banco_id):
    db.query(Inventario).filter(Inventario.banco_id == banco_id).delete()
    db.commit()
