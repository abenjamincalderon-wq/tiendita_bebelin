from flask import Flask

app = Flask(__name__)

@app.route("/")
def inicio():
    return "PrecioCerca funciona correctamente"

if __name__ == "__main__":
    print("INICIANDO PRECIOCERCA")
    app.run(debug=True)