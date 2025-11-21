// Registrar donación
const formDonante = document.getElementById("form-donante");
if (formDonante) {
    formDonante.addEventListener("submit", async (e) => {
        e.preventDefault();

        const data = {
            nombre: document.getElementById("nombre").value,
            tipo: document.getElementById("tipo").value.trim().toLowerCase(), // normalizamos tipo
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

        // 👇 refresca la tabla de bancos para ver inventario actualizado
        cargarBancos();
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

        // 👇 refresca la tabla de bancos
        cargarBancos();
    });
}


// Limpiar inventario por ID
const formLimpiar = document.getElementById("form-limpiar");
if (formLimpiar) {
    formLimpiar.addEventListener("submit", async (e) => {
        e.preventDefault();

        const id = document.getElementById("banco-id-limpiar").value; // 👈 ahora usamos id
        if (!id) {
            alert("Por favor ingresa el ID del banco a limpiar");
            return;
        }

        const res = await fetch(`/bancos/${encodeURIComponent(id)}/limpiar`, {
            method: "DELETE"
        });

        const r = await res.json();
        document.getElementById("respuesta-prop").innerText = r.mensaje;

        // 👇 refresca la tabla
        cargarBancos();
    });
}


// Eliminar banco por ID
const formEliminar = document.getElementById("form-eliminar");
if (formEliminar) {
    formEliminar.addEventListener("submit", async (e) => {
        e.preventDefault();

        const id = document.getElementById("banco-id-eliminar").value; // 👈 ahora usamos id
        if (!id) {
            alert("Por favor ingresa el ID del banco a eliminar");
            return;
        }

        const res = await fetch(`/bancos/eliminar/${encodeURIComponent(id)}`, {
            method: "DELETE"
        });

        const r = await res.json();
        document.getElementById("respuesta-prop").innerText = r.mensaje;

        // 👇 refresca la tabla
        cargarBancos();
    });
}