from models import Banco, Inventario, Donacion

def asignar_banco(db, alimento, cantidad):
    bancos = db.query(Banco).all()
    mejor_banco = None
    menor_cantidad = 9999999

    for banco in bancos:
        inv = (
            db.query(Inventario)
            .filter(Inventario.banco_id == banco.id, Inventario.alimento == alimento)
            .first()
        )

        cant = inv.cantidad if inv else 0

        if cant < banco.capacidad_total and cant < menor_cantidad:
            menor_cantidad = cant
            mejor_banco = banco

    return mejor_banco

def registrar_donacion(db, donacion):
    banco = asignar_banco(db, donacion.alimento, donacion.cantidad)

    if not banco:
        return None

    inv = (
        db.query(Inventario)
        .filter(Inventario.banco_id == banco.id, Inventario.alimento == donacion.alimento)
        .first()
    )

    if inv:
        inv.cantidad += donacion.cantidad
    else:
        inv = Inventario(
            banco_id=banco.id,
            alimento=donacion.alimento,
            cantidad=donacion.cantidad
        )
        db.add(inv)

    nueva = Donacion(
        usuario_id=donacion.usuario_id,
        alimento=donacion.alimento,
        cantidad=donacion.cantidad,
        banco_asignado=banco.id
    )

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return nueva, banco
