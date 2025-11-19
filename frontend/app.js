// Registrar donación
const formDonante = document.getElementById("form-donante");
if (formDonante) {
    formDonante.addEventListener("submit", async (e) => {
        e.preventDefault();

        const data = {
            nombre: document.getElementById("nombre").value,
            tipo: document.getElementById("tipo").value,
            cantidad: parseInt(document.getElementById("cantidad").value)
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
            direccion: document.getElementById("banco-direccion").value
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

// Limpiar inventario
const formLimpiar = document.getElementById("form-limpiar");
if (formLimpiar) {
    formLimpiar.addEventListener("submit", async (e) => {
        e.preventDefault();

        const id = document.getElementById("banco-id").value;

        const res = await fetch(`/bancos/${id}/limpiar`, {
            method: "DELETE"
        });

        const r = await res.json();
        document.getElementById("respuesta-prop").innerText = r.mensaje;
    });
}
