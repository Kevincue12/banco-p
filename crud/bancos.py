from models import Banco
from sqlalchemy.orm import Session


def crear_banco(db, banco_data):
    categorias_default = {
        "frutas": {"capacidad": banco_data.capacidad_total, "usado": 0},
        "granos": {"capacidad": banco_data.capacidad_total, "usado": 0},
        "enlatados": {"capacidad": banco_data.capacidad_total, "usado": 0},
    }

    nuevo_banco = Banco(
        nombre=banco_data.nombre,
        direccion=banco_data.direccion,
        capacidad_total=banco_data.capacidad_total,
        categorias=categorias_default
    )
    db.add(nuevo_banco)
    db.commit()
    db.refresh(nuevo_banco)
    return nuevo_banco



def limpiar_inventario(db: Session, banco_id: int):
    banco = db.query(Banco).filter(Banco.id == banco_id).first()
    if not banco:
        return None

    for categoria in banco.categorias.values():
        categoria["usado"] = 0

    banco.categorias = banco.categorias
    db.commit()
    return banco
