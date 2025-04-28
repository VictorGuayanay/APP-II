from flask import Flask # You

app = Flask(__name__)

@app.route("/")
def hello():
    return "¡Entorno Flask funcionando!"

if __name__ == "__main__":
    app.run(debug=True)