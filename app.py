
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from database import init_db, buscar_precio, guardar_precio
import requests

app = Flask(__name__)
app.secret_key = "tiendita-bebelin-clave-local"

# Crear la base de datos
init_db()


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/api/negocios")
def obtener_negocios():

    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    producto = request.args.get("producto", "pan").strip()

    if lat is None or lon is None:
        return jsonify({
            "error": "No se recibieron coordenadas"
        }), 400

    if not producto:
        producto = "pan"

    consulta = f"""
    [out:json][timeout:25];
    (
      node["shop"](around:3000,{lat},{lon});
      way["shop"](around:3000,{lat},{lon});
      relation["shop"](around:3000,{lat},{lon});
    );
    out center tags;
    """

    servidores = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter"
    ]

    datos = None

    for servidor in servidores:
        try:
            respuesta = requests.post(
                servidor,
                data={"data": consulta},
                headers={
                    "User-Agent": "TienditaBebelin/1.0"
                },
                timeout=45
            )

            respuesta.raise_for_status()
            datos = respuesta.json()
            break

        except (requests.RequestException, ValueError) as error:
            print(f"Error consultando {servidor}: {error}")

    if datos is None:
        return jsonify({
            "error": "No se pudieron consultar los negocios. Intenta nuevamente."
        }), 503

    negocios = []

    for elemento in datos.get("elements", []):

        etiquetas = elemento.get("tags", {})
        nombre = etiquetas.get("name", "Negocio sin nombre")

        if "lat" in elemento:
            latitud = elemento["lat"]
            longitud = elemento["lon"]

        elif "center" in elemento:
            latitud = elemento["center"]["lat"]
            longitud = elemento["center"]["lon"]

        else:
            continue

        direccion = etiquetas.get(
            "addr:street",
            "Dirección no informada"
        )

        precio = buscar_precio(nombre, producto)

        negocios.append({
            "nombre": nombre,
            "lat": latitud,
            "lon": longitud,
            "direccion": direccion,
            "producto": producto,
            "precio": precio
        })

    return jsonify(negocios)


@app.route("/negocio", methods=["GET", "POST"])
def negocio():

    if request.method == "POST":

        nombre = request.form.get("nombre", "").strip()
        producto = request.form.get("producto", "").strip()
        precio = request.form.get("precio", type=int)
        direccion = request.form.get("direccion", "").strip()

        if (
            not nombre
            or not producto
            or precio is None
            or precio <= 0
            or not direccion
        ):
            flash("Completa todos los campos con información válida.")
            return redirect(url_for("negocio"))

        guardar_precio(
            nombre,
            producto,
            precio,
            direccion
        )

        flash("¡Precio registrado correctamente en Tiendita Bebelín!")

        return redirect(url_for("inicio"))

    return render_template("negocio.html")


if __name__ == "__main__":
    print("INICIANDO TIENDITA BEBELÍN")
    app.run(debug=True)
