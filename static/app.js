// Registrar donación
const formDonante = document.getElementById("form-donante");
if (formDonante) {
    formDonante.addEventListener("submit", async (e) => {
        e.preventDefault();

        const data = {
            nombre: document.getElementById("nombre").value,
            tipo: document.getElementById("tipo").value,   // ya no necesitas "alimento" duplicado
            cantidad: parseInt(document.getElementById("cantidad").value),
            usuario_id: 1
        };

        const res = await fetch("/donar/", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        });

        const r = await res.json();
        document.getElementById("respuesta").innerText = r.mensaje;
    });
}


// Registrar banco
const formBanco = document.getElementById("form-banco");
if (formBanco) {
    formBanco.addEventListener("submit", async (e) => {
        e.preventDefault();

        const data = {
            nombre: document.getElementById("banco-nombre").value,
            direccion: document.getElementById("banco-direccion").value,
            capacidad_total: parseInt(document.getElementById("banco-capacidad").value)
        };

        const res = await fetch("/bancos/", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        });

        const r = await res.json();
        document.getElementById("respuesta-prop").innerText = r.mensaje || "Banco registrado.";
    });
}


// Limpiar inventario por nombre
const formLimpiar = document.getElementById("form-limpiar");
if (formLimpiar) {
    formLimpiar.addEventListener("submit", async (e) => {
        e.preventDefault();

        const nombre = document.getElementById("banco-nombre-limpiar").value; // 👈 usa nombre, no id
        if (!nombre) {
            alert("Por favor ingresa el nombre del banco a limpiar");
            return;
        }

        const res = await fetch(`/bancos/${encodeURIComponent(nombre)}/limpiar`, {
            method: "DELETE"
        });

        const r = await res.json();
        document.getElementById("respuesta-prop").innerText = r.mensaje;
    });
}


// Eliminar banco por nombre
const formEliminar = document.getElementById("form-eliminar");
if (formEliminar) {
    formEliminar.addEventListener("submit", async (e) => {
        e.preventDefault();

        const nombre = document.getElementById("banco-nombre-eliminar").value;
        if (!nombre) {
            alert("Por favor ingresa el nombre del banco a eliminar");
            return;
        }

        const res = await fetch(`/bancos/eliminar/${encodeURIComponent(nombre)}`, {
            method: "DELETE"
        });

        const r = await res.json();
        document.getElementById("respuesta-prop").innerText = r.mensaje;
    });
}