import os
import tempfile

from flask import Flask, render_template, request

from fuentes.word import extraer_texto_docx
from generador import (
    cargar_contexto_base,
    generar_carta,
    generar_mane,
    guardar_salida,
)


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    generated = None
    error = None
    data = None
    if request.method == "POST":
        try:
            fecha_iso = request.form.get("fecha")
            action = request.form.get("action")
            data = cargar_contexto_base(fecha_iso)

            vida_parroquial = request.form.get("vida_parroquial", "").strip()
            uploaded = request.files.get("vida_docx")
            if uploaded and uploaded.filename:
                suffix = os.path.splitext(uploaded.filename)[1].lower()
                if suffix != ".docx":
                    raise ValueError("El archivo de Vida Parroquial debe ser .docx")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                    uploaded.save(tmp.name)
                    vida_parroquial = extraer_texto_docx(tmp.name)
                os.unlink(tmp.name)

            data["carta"] = request.form.get("carta") or generar_carta(data["config"], data["liturgia"])
            data["mane"] = request.form.get("mane") or generar_mane(data["config"], data["liturgia"])
            data["vida_parroquial"] = vida_parroquial

            selected_santos = request.form.getlist("santos_seleccionados")
            santos_data = []
            from fuentes.ia import generar_imagen_dalle
            for santo in selected_santos:
                img_path = generar_imagen_dalle(santo)
                santos_data.append({
                    "nombre": santo,
                    "imagen": img_path
                })
            data["santos_seleccionados"] = santos_data

            if action == "save":
                md_path, html_path = guardar_salida(data, avanzar_estado=True)
                generated = {
                    "md": md_path,
                    "html": html_path,
                    "numero": data["numero_assumpta"],
                    "fecha": data["fecha_iso"]
                }
        except Exception as exc:
            error = str(exc)
    return render_template("index.html", data=data, generated=generated, error=error)


@app.route("/triptico/<numero>/<fecha>")
def triptico(numero, fecha):
    import json
    json_filename = f"assumpta-{numero}-{fecha}.json"
    json_path = os.path.join(os.path.dirname(__file__), "output", json_filename)
    if not os.path.exists(json_path):
        return f"No se encontró el borrador para el número {numero} y fecha {fecha}.", 404
    with open(json_path, "r", encoding="utf-8") as f:
        bulletin_data = json.load(f)
    return render_template("triptico.html", data=bulletin_data)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

