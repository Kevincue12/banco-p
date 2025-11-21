from models import Donacion, Banco
from sqlalchemy.orm import Session


def registrar_donacion(db: Session, data):
    bancos = db.query(Banco).all()

    for banco in bancos:
        if data.tipo not in banco.categorias:
            continue

        categoria = banco.categorias[data.tipo]

        if categoria["usado"] + data.cantidad <= categoria["capacidad"]:
            categoria["usado"] += data.cantidad
            banco.categorias = banco.categorias

            nueva = Donacion(
                usuario_id=data.usuario_id,
                alimento=data.alimento,
                cantidad=data.cantidad,
                banco_asignado=banco.id
            )

            db.add(nueva)
            db.commit()
            db.refresh(nueva)

            return nueva, banco

    return None
