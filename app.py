import os
import tempfile
import base64

from flask import Flask, render_template, request

from fuentes.word import extraer_texto_docx
from generador import (
    cargar_contexto_base,
    generar_carta,
    generar_mane,
    generar_salida,
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
            
            n_assumpta_str = request.form.get("numero_assumpta")
            n_compendio_str = request.form.get("numero_compendio")
            n_assumpta = int(n_assumpta_str) if n_assumpta_str else None
            n_compendio = int(n_compendio_str) if n_compendio_str else None
            
            data = cargar_contexto_base(fecha_iso, n_assumpta, n_compendio)

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

            libro_titulo = request.form.get("libro_titulo", "").strip()
            libro_autor = request.form.get("libro_autor", "").strip()
            libro_texto = request.form.get("libro_texto", "").strip()
            
            uploaded_libro_doc = request.files.get("libro_doc")
            if uploaded_libro_doc and uploaded_libro_doc.filename:
                suffix = os.path.splitext(uploaded_libro_doc.filename)[1].lower()
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    uploaded_libro_doc.save(tmp.name)
                    if suffix == ".docx":
                        from fuentes.word import extraer_texto_docx
                        libro_texto = extraer_texto_docx(tmp.name)
                    elif suffix == ".pdf":
                        from pypdf import PdfReader
                        reader = PdfReader(tmp.name)
                        libro_texto = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
                os.unlink(tmp.name)
            
            uploaded_libro_img = request.files.get("libro_img")
            libro_img_b64 = request.form.get("libro_img_b64")
            if uploaded_libro_img and uploaded_libro_img.filename:
                img_data = uploaded_libro_img.read()
                libro_img_b64 = "data:image/png;base64," + base64.b64encode(img_data).decode("utf-8")

            data["libro_titulo"] = libro_titulo
            data["libro_autor"] = libro_autor
            data["libro_texto"] = libro_texto
            data["libro_img_b64"] = libro_img_b64

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

            if action == "preview_triptico":
                return render_template("triptico.html", data=data)

            if action == "save":
                md, html_text = generar_salida(data, avanzar_estado=True)
                b64_md = base64.b64encode(md.encode('utf-8')).decode('utf-8')
                b64_html = base64.b64encode(html_text.encode('utf-8')).decode('utf-8')
                
                generated = {
                    "md": b64_md,
                    "html": b64_html,
                    "numero": data["numero_assumpta"],
                    "fecha": data["fecha_iso"]
                }
                data["numero_assumpta"] += 1
                data["numero_compendio"] += 1

        except Exception as exc:
            error = str(exc)
    return render_template("index.html", data=data, generated=generated, error=error)


@app.route("/triptico/<numero>/<fecha>")
def triptico(numero, fecha):
    return "En Vercel (Serverless), usa el botón 'Vista Previa del Tríptico' del formulario. Los archivos temporales no se guardan.", 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

