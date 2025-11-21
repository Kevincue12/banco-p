from models import Usuario

def crear_usuario(db, usuario):
    nuevo = Usuario(
        nombre=usuario.nombre,
        correo=usuario.correo,
        tipo_usuario=usuario.tipo_usuario
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo
