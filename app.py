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

            if action == "save":
                md_path, html_path = guardar_salida(data, avanzar_estado=True)
                generated = {"md": md_path, "html": html_path}
        except Exception as exc:
            error = str(exc)
    return render_template("index.html", data=data, generated=generated, error=error)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
