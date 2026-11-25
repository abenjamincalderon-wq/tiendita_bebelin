const ubicacionInicial = [-37.4697, -72.3537];

const mapa = L.map("mapa").setView(ubicacionInicial, 14);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap"
}).addTo(mapa);

let marcadorUsuario = L.marker(ubicacionInicial)
    .addTo(mapa)
    .bindPopup("Ubicación de referencia");

let marcadoresNegocios = [];

const buscador = document.getElementById("buscarProducto");
const botonBuscar = document.getElementById("btnBuscar");
const listaNegocios = document.getElementById("listaNegocios");

let latUsuario = ubicacionInicial[0];
let lonUsuario = ubicacionInicial[1];

function limpiarMarcadores() {
    marcadoresNegocios.forEach(marcador => mapa.removeLayer(marcador));
    marcadoresNegocios = [];
}

function formatoPrecio(precio) {
    if (precio === null || precio === undefined) {
        return "Sin precio informado";
    }

    return "$" + Number(precio).toLocaleString("es-CL");
}

function mostrarNegocios(negocios) {
    limpiarMarcadores();
    listaNegocios.replaceChildren();

    if (negocios.length === 0) {
        listaNegocios.textContent =
            "No se encontraron negocios cercanos.";
        return;
    }

    negocios.forEach(negocio => {
        const precio = formatoPrecio(negocio.precio);

        // Crear tarjeta del negocio
        const tarjeta = document.createElement("article");
        tarjeta.className = "tarjeta-negocio";

        const titulo = document.createElement("h3");
        titulo.textContent = negocio.nombre;

        const precioTexto = document.createElement("p");
        precioTexto.className = "precio";
        precioTexto.textContent =
            negocio.producto + ": " + precio;

        const direccion = document.createElement("p");
        direccion.textContent = negocio.direccion;

        tarjeta.append(titulo, precioTexto, direccion);
        listaNegocios.appendChild(tarjeta);

        // Crear marcador en el mapa
        const marcador = L.marker([
            negocio.lat,
            negocio.lon
        ]).addTo(mapa);

        marcador.bindPopup(
            `<strong>${escapeHTML(negocio.nombre)}</strong><br>` +
            `${escapeHTML(negocio.producto)}: ${escapeHTML(precio)}<br>` +
            `${escapeHTML(negocio.direccion)}`
        );

        marcadoresNegocios.push(marcador);
    });
}

function escapeHTML(texto) {
    return String(texto).replace(/[&<>"']/g, caracter => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    })[caracter]);
}

async function buscarNegocios() {
    const producto = buscador.value.trim() || "pan";

    listaNegocios.textContent = "Buscando negocios cercanos...";

    try {
        const respuesta = await fetch(
            `/api/negocios?lat=${latUsuario}&lon=${lonUsuario}&producto=${encodeURIComponent(producto)}`
        );

        if (!respuesta.ok) {
            throw new Error("No se pudo consultar los negocios.");
        }

        const negocios = await respuesta.json();
        mostrarNegocios(negocios);

    } catch (error) {
        listaNegocios.textContent =
            "No fue posible cargar los negocios. Intenta nuevamente.";

        console.error(error);
    }
}

botonBuscar.addEventListener("click", buscarNegocios);

buscador.addEventListener("keydown", evento => {
    if (evento.key === "Enter") {
        buscarNegocios();
    }
});

// Solicitar ubicación al usuario
if ("geolocation" in navigator) {
    navigator.geolocation.getCurrentPosition(
        posicion => {
            latUsuario = posicion.coords.latitude;
            lonUsuario = posicion.coords.longitude;

            mapa.setView([latUsuario, lonUsuario], 15);

            marcadorUsuario.setLatLng([latUsuario, lonUsuario])
                .bindPopup("Tu ubicación");

            buscarNegocios();
        },
        () => {
            console.log("Se mantiene la ubicación de referencia.");
            buscarNegocios();
        }
    );
} else {
    buscarNegocios();
}