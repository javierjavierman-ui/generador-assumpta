from __future__ import annotations

import base64
import html
import os
import uuid
import warnings
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

warnings.filterwarnings("ignore", category=DeprecationWarning)

import cgi

from assumpta_core import (
    extract_compendio_questions,
    extract_docx_text,
    fetch_vatican_gospel,
    generate_assumpta,
    generate_pastor_letter,
    gospel_title_from_ref,
    load_state,
    long_spanish_date,
    next_assumpta_number,
    saints_for_week,
    save_state,
    suggested_liturgy_image_query,
)


BASE_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(BASE_DIR, "assets", "uploads")
ACTIVE_TUNNEL_PATH = os.path.join(BASE_DIR, "active_tunnel_url.txt")
DEFAULT_COMPENDIO = os.environ.get("ASSUMPTA_COMPENDIO", os.path.join(BASE_DIR, "Compendio.pdf"))
AUTH_USERNAME = "pasuntorre"
AUTH_PASSWORD = "pasuntorre26.."
FIXED_ALELUYA = "R. Aleluya, aleluya, aleluya. Yo soy el pan vivo que ha bajado del cielo -dice el Señor-; el que coma de este pan vivirá para siempre. R."
SIMULATION_1233 = {
    "sim": "1233",
    "fecha": "2026-06-07",
    "numero": 1233,
    "compendio_start": 325,
    "celebracion": "Corpus Christi",
    "lecturas": "Dt 8, 2-3. 14b-16a     1Cor 10, 16-17",
    "evangelio_ref": "Juan 6, 51-58",
    "liturgia_imagen_query": "Eucharist chalice bread",
}


def esc(value: object) -> str:
    return html.escape(str(value or ""))


def read_field(form: cgi.FieldStorage, name: str, default: str = "") -> str:
    item = form[name] if name in form else None
    if item is None:
        return default
    if isinstance(item, list):
        item = item[0]
    value = item.value
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    return value


def read_upload(form: cgi.FieldStorage, name: str) -> bytes:
    item = form[name] if name in form else None
    if item is None or isinstance(item, list) or not getattr(item, "filename", ""):
        return b""
    return item.file.read()


def save_image_upload(form: cgi.FieldStorage, name: str, prefix: str) -> str:
    item = form[name] if name in form else None
    if item is None or isinstance(item, list) or not getattr(item, "filename", ""):
        return ""
    filename = os.path.basename(item.filename or "")
    ext = os.path.splitext(filename)[1].lower()
    if ext not in {".jpg", ".jpeg", ".png", ".gif"}:
        return ""
    data = item.file.read()
    if not data:
        return ""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    path = os.path.join(UPLOAD_DIR, f"{prefix}-{uuid.uuid4().hex}{ext}")
    with open(path, "wb") as f:
        f.write(data)
    return path


def safe_upload_path(value: str) -> str:
    if not value:
        return ""
    path = os.path.abspath(value)
    upload_root = os.path.abspath(UPLOAD_DIR)
    if path.startswith(upload_root) and os.path.exists(path):
        return path
    return ""


class Handler(BaseHTTPRequestHandler):
    def is_authenticated(self) -> bool:
        header = self.headers.get("Authorization", "")
        if not header.startswith("Basic "):
            return False
        try:
            decoded = base64.b64decode(header.split(" ", 1)[1]).decode("utf-8")
        except Exception:
            return False
        return decoded == f"{AUTH_USERNAME}:{AUTH_PASSWORD}"

    def require_auth(self) -> bool:
        if self.is_authenticated():
            return True
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="Generador Assumpta"')
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("Acceso protegido al Generador Assumpta.".encode("utf-8"))
        return False

    def do_GET(self):
        if not self.require_auth():
            return
        parsed = urlparse(self.path)
        if parsed.path == "/static/style.css" or parsed.path.startswith("/static/previews/"):
            return self.serve_static()
        if parsed.path.startswith("/output/"):
            return self.serve_output()
        query = parse_qs(parsed.query)
        simulation = query.get("sim", [""])[0] == "1233"
        return self.render_form(data=self.simulation_defaults() if simulation else None, simulation=simulation)

    def do_POST(self):
        if not self.require_auth():
            return
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={
            "REQUEST_METHOD": "POST",
            "CONTENT_TYPE": self.headers.get("Content-Type", ""),
        })
        simulation = read_field(form, "simulation") == "1233"
        action = read_field(form, "action", "proof")
        proof = action != "production"
        result, data, next_question = self.build_result_from_form(form, simulation=simulation, proof=proof)
        if action == "production" and read_field(form, "advance_state") == "yes" and not simulation:
            save_state({
                "last_assumpta_number": data["numero"],
                "last_assumpta_date": data["fecha"],
                "next_compendio_question": next_question,
            })
        self.render_form(result=result, data=data, next_question=next_question, simulation=simulation)

    def simulation_defaults(self) -> dict:
        return {
            "simulation": "1233",
            "fecha": SIMULATION_1233["fecha"],
            "fecha_larga": long_spanish_date(SIMULATION_1233["fecha"]).upper(),
            "numero": SIMULATION_1233["numero"],
            "compendio_start": SIMULATION_1233["compendio_start"],
            "celebracion": SIMULATION_1233["celebracion"],
            "lecturas": SIMULATION_1233["lecturas"],
            "evangelio_ref": SIMULATION_1233["evangelio_ref"],
            "evangelio_titulo": gospel_title_from_ref(SIMULATION_1233["evangelio_ref"]),
            "liturgia_imagen_query": SIMULATION_1233["liturgia_imagen_query"],
            "liturgia_imagen_path": "",
            "lleva_secuencia": "",
            "carta": "",
            "secuencia": "",
            "evangelio": "",
            "anuncio": "",
            "anuncio_imagen_path": "",
            "habla_papa": "",
            "santos": ["Bernabe", "Antonio de Padua"],
        }

    def build_result_from_form(self, form: cgi.FieldStorage, simulation: bool = False, proof: bool = True) -> tuple[dict, dict, int]:
        defaults = self.simulation_defaults() if simulation else {}
        fecha = read_field(form, "fecha", defaults.get("fecha", "2026-06-14"))
        numero = int(read_field(form, "numero", str(defaults.get("numero", next_assumpta_number()))))
        compendio_default = defaults.get("compendio_start", load_state().get("next_compendio_question", 330))
        compendio_start = int(read_field(form, "compendio_start", str(compendio_default)))
        compendio, next_question = extract_compendio_questions(DEFAULT_COMPENDIO, compendio_start)
        gospel = fetch_vatican_gospel(fecha)

        carta = extract_docx_text(read_upload(form, "carta_docx")) or read_field(form, "carta")
        lleva_secuencia = read_field(form, "lleva_secuencia") == "yes"
        secuencia = ""
        if lleva_secuencia:
            secuencia = extract_docx_text(read_upload(form, "secuencia_docx")) or read_field(form, "secuencia")
        anuncio = extract_docx_text(read_upload(form, "anuncio_docx")) or read_field(form, "anuncio")
        anuncio_imagen_path = save_image_upload(form, "anuncio_imagen", "anuncio") or safe_upload_path(read_field(form, "anuncio_imagen_path"))
        liturgia_imagen_path = save_image_upload(form, "liturgia_imagen", "liturgia") or safe_upload_path(read_field(form, "liturgia_imagen_path"))
        habla_papa = extract_docx_text(read_upload(form, "papa_docx")) or read_field(form, "habla_papa")
        selected_saints = form.getlist("saints") if "saints" in form else []
        celebration = read_field(form, "celebracion") or gospel.celebration
        evangelio_ref = read_field(form, "evangelio_ref") or gospel.gospel_ref
        carta = carta or generate_pastor_letter(celebration, evangelio_ref)
        image_query = read_field(form, "liturgia_imagen_query") or suggested_liturgy_image_query(gospel)

        data = {
            "fecha": fecha,
            "fecha_larga": long_spanish_date(fecha).upper(),
            "numero": numero,
            "carta": carta or "Pegue o cargue la carta del parroco.",
            "compendio": compendio,
            "simulation": "1233" if simulation else "",
            "celebracion": celebration,
            "lecturas": read_field(form, "lecturas") or gospel.reading_ref,
            "lleva_secuencia": "yes" if lleva_secuencia else "",
            "secuencia": secuencia,
            "aleluya": gospel.aleluya or FIXED_ALELUYA,
            "evangelio_ref": evangelio_ref,
            "evangelio_titulo": gospel_title_from_ref(evangelio_ref),
            "evangelio": read_field(form, "evangelio") or gospel.gospel_text,
            "evangelio_url": gospel.source_url,
            "evangelio_warning": gospel.warning,
            "liturgia_imagen_query": image_query,
            "liturgia_imagen_path": liturgia_imagen_path,
            "anuncio": anuncio or "Cargue el Word del anuncio semanal.",
            "anuncio_imagen_path": anuncio_imagen_path,
            "habla_papa": habla_papa or "Cargue el Word de Habla el Papa.",
            "santos": selected_saints,
            "proof": proof,
        }
        result = generate_assumpta(data, proof=proof)
        return result, data, next_question

    def serve_static(self):
        rel = urlparse(self.path).path.lstrip("/")
        path = os.path.abspath(os.path.join(BASE_DIR, rel))
        static_root = os.path.abspath(os.path.join(BASE_DIR, "static"))
        if not path.startswith(static_root) or not os.path.exists(path):
            self.send_error(404)
            return
        if path.endswith(".css"):
            content_type = "text/css; charset=utf-8"
        elif path.endswith(".jpg") or path.endswith(".jpeg"):
            content_type = "image/jpeg"
        else:
            content_type = "image/png"
        with open(path, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def serve_output(self):
        rel = urlparse(self.path).path.lstrip("/")
        path = os.path.abspath(os.path.join(BASE_DIR, rel))
        output_root = os.path.abspath(os.path.join(BASE_DIR, "output"))
        if not path.startswith(output_root) or not os.path.exists(path):
            self.send_error(404)
            return
        with open(path, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "application/pdf")
        self.send_header("Content-Disposition", f"inline; filename={os.path.basename(path)}")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def render_form(self, result: dict | None = None, data: dict | None = None, next_question: int | None = None, simulation: bool = False):
        state = load_state()
        defaults = self.simulation_defaults() if simulation and not data else {}
        view_data = data or defaults
        fecha = view_data.get("fecha", "2026-06-14")
        saints = saints_for_week(fecha)
        saint_checks = "\n".join(
            f"<label class='check'><input type='checkbox' name='saints' value='{esc(s['name'])}'> "
            f"<span>{esc(s['date'])}</span><strong>{esc(s['name'])}</strong></label>"
            for s in saints
        )
        for selected in view_data.get("santos", []) or []:
            saint_checks = saint_checks.replace(
                f"name='saints' value='{esc(selected)}'",
                f"name='saints' value='{esc(selected)}' checked",
            )
        sim_banner = ""
        sim_hidden = ""
        state_control = '<label class="inline"><input type="checkbox" name="advance_state" value="yes"> Actualizar estado si el PDF queda bien</label>'
        if simulation:
            sim_banner = "<section class='notice'><strong>Simulacion boletin 1233.</strong> Esta prueba no actualiza el estado semanal real.</section>"
            sim_hidden = "<input type='hidden' name='simulation' value='1233'>"
            state_control = "<p class='muted'>Modo simulacion: el estado semanal no se actualizara.</p>"
        share_html = self.render_share_box()
        preview_html = ""
        if result:
            pdf_rel = os.path.relpath(result["pdf"], BASE_DIR)
            warnings_html = "".join(f"<li>{esc(w)}</li>" for w in result.get("warnings", []))
            cache_key = str(int(os.path.getmtime(result["pdf"])))
            previews = "".join(f"<img src='{esc(path)}?v={cache_key}' alt='Previsualizacion del triptico'>" for path in result.get("previews", []))
            first_preview = result.get("previews", [""])[0]
            preview_link = f"<a class='button-link secondary' href='{esc(first_preview)}?v={cache_key}' target='_blank'>Abrir preview en ventana nueva</a>" if first_preview else ""
            warning_block = f"<ul class='warnings'>{warnings_html}</ul>" if warnings_html else "<p class='ok'>Todo parece caber en la plantilla.</p>"
            kind = "prueba con marca" if result.get("pdf", "").endswith("-prueba.pdf") else "produccion limpia"
            preview_html = f"""
      <section class="preview" id="preview">
        <h2>8. Previsualizacion</h2>
        <p class="muted">Version generada: {esc(kind)}</p>
        {warning_block}
        <div class="preview-actions">{preview_link}<a class="button-link" href="/{esc(pdf_rel)}" target="_blank">Abrir PDF para imprimir</a></div>
        <div class="preview-pages">{previews}</div>
        <p class="muted">Siguiente pregunta sugerida del Compendio: {esc(next_question)}</p>
      </section>"""

        body = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Generador Assumpta</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <main>
    <header class="top">
      <div>
        <p class="eyebrow">Hoja parroquial</p>
        <h1>Generador Assumpta</h1>
      </div>
      <p class="badge">Plantilla visual exacta</p>
    </header>
    <nav class="modebar">
      <a href="/">Modo normal</a>
      <a href="/?sim=1233">Simular boletin 1233</a>
    </nav>
    {sim_banner}
    {share_html}

    <form method="post" enctype="multipart/form-data">
      {sim_hidden}
      <section>
        <h2>1. Fecha</h2>
        <div class="grid">
          <label>Domingo del folleto <input type="date" name="fecha" value="{esc(fecha)}"></label>
          <label>Numero Assumpta <input type="number" name="numero" value="{esc(view_data.get('numero', next_assumpta_number()))}"></label>
          <label>Pregunta inicial Compendio <input type="number" name="compendio_start" value="{esc(view_data.get('compendio_start', state.get('next_compendio_question', 330)))}"></label>
        </div>
      </section>

      <section>
        <h2>2. Carta del parroco</h2>
        <p class="muted">Si dejas este apartado vacio, la app propondra un borrador pastoral breve.</p>
        <input type="file" name="carta_docx" accept=".docx">
        <textarea name="carta" rows="7" placeholder="O pega aqui la carta si no tienes Word">{esc((data or {}).get('carta', ''))}</textarea>
      </section>

      <section>
        <h2>3. Catecismo</h2>
        <p class="muted">La app lee el Compendio desde la pregunta inicial y coloca las preguntas que caben.</p>
      </section>

      <section>
        <h2>4. Evangelio y liturgia</h2>
        <div class="grid">
          <label>Titulo liturgico <input name="celebracion" value="{esc(view_data.get('celebracion', ''))}" placeholder="Se rellenara desde Vatican News"></label>
          <label>Lecturas <input name="lecturas" value="{esc(view_data.get('lecturas', ''))}" placeholder="Ej.: Hch..., Sal..., Jn..."></label>
          <label>Referencia Evangelio <input name="evangelio_ref" value="{esc(view_data.get('evangelio_ref', ''))}" placeholder="Se rellenara automaticamente"></label>
        </div>
        <label class="inline"><input type="checkbox" name="lleva_secuencia" value="yes" {'checked' if view_data.get('lleva_secuencia') == 'yes' else ''}> Este boletin lleva Secuencia</label>
        <label>Secuencia desde Word <input type="file" name="secuencia_docx" accept=".docx"></label>
        <label>Secuencia <textarea name="secuencia" rows="5" placeholder="Solo rellenar si este boletin lleva Secuencia">{esc((data or {}).get('secuencia', ''))}</textarea></label>
        <label>Evangelio <textarea name="evangelio" rows="8" placeholder="Se rellenara desde Oracion y Liturgia; puedes corregirlo si hace falta">{esc((data or {}).get('evangelio', ''))}</textarea></label>
        <label>Imagen del Evangelio <input type="file" name="liturgia_imagen" accept="image/*"></label>
        <input type="hidden" name="liturgia_imagen_path" value="{esc((data or {}).get('liturgia_imagen_path', ''))}">
        {"<p class='muted'>Imagen liturgica cargada. Si subes otra, se sustituira.</p>" if (data or {}).get('liturgia_imagen_path') else ""}
        <label>Imagen propuesta por la app <input name="liturgia_imagen_query" value="{esc(view_data.get('liturgia_imagen_query', ''))}" placeholder="Ej.: Eucharist chalice bread"></label>
        <p class="muted">Fuente liturgica: Oracion y Liturgia - Archimadrid.</p>
        <p class="muted">Antes del texto se imprimira automaticamente: {esc((data or {}).get('evangelio_titulo', 'Santo Evangelio según...'))}</p>
      </section>

      <section>
        <h2>5. Anuncio central</h2>
        <input type="file" name="anuncio_docx" accept=".docx">
        <label>Imagen del anuncio <input type="file" name="anuncio_imagen" accept="image/*"></label>
        <input type="hidden" name="anuncio_imagen_path" value="{esc((data or {}).get('anuncio_imagen_path', ''))}">
        {"<p class='muted'>Imagen del anuncio cargada. Si subes otra, se sustituira.</p>" if (data or {}).get('anuncio_imagen_path') else ""}
        <textarea name="anuncio" rows="5" placeholder="O pega aqui el anuncio central">{esc((data or {}).get('anuncio', ''))}</textarea>
      </section>

      <section>
        <h2>6. Habla el Papa</h2>
        <input type="file" name="papa_docx" accept=".docx">
        <textarea name="habla_papa" rows="7" placeholder="O pega aqui el texto de Habla el Papa">{esc((data or {}).get('habla_papa', ''))}</textarea>
      </section>

      <section>
        <h2>7. Santos</h2>
        <p class="muted">Elige uno o dos. La app descargara las imagenes automaticamente al previsualizar.</p>
        <div class="checks">{saint_checks}</div>
      </section>

      <div class="actions">
        <button type="submit" name="action" value="proof">Imprimir prueba</button>
        <button type="submit" name="action" value="production">Generar produccion</button>
        {state_control}
      </div>
    </form>
    {preview_html}
  </main>
</body>
</html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def render_share_box(self) -> str:
        url = ""
        if os.path.exists(ACTIVE_TUNNEL_PATH):
            with open(ACTIVE_TUNNEL_PATH, "r", encoding="utf-8") as f:
                url = f.read().strip()
        if url:
            return (
                "<section class='notice'><strong>Compartir app.</strong> "
                f"URL activa: <a href='{esc(url)}' target='_blank'>{esc(url)}</a>. "
                "Si deja de funcionar, genere una URL nueva con el modo compartir.</section>"
            )
        return (
            "<section class='notice'><strong>Compartir app.</strong> "
            "No hay URL publica activa. Ejecute el modo compartir para crear una URL temporal renovable.</section>"
        )


def main():
    host = os.environ.get("ASSUMPTA_HOST", "127.0.0.1")
    start_port = int(os.environ.get("ASSUMPTA_PORT", "5000"))
    for port in range(start_port, start_port + 10):
        try:
            server = ThreadingHTTPServer((host, port), Handler)
            print(f"Generador Assumpta disponible en http://{host}:{port}")
            if host == "0.0.0.0":
                print("Modo compartido activo. Use un tunel temporal hacia este puerto para obtener una URL publica.")
            server.serve_forever()
            return
        except OSError:
            continue
    raise RuntimeError("No hay puertos disponibles entre 5000 y 5009.")


if __name__ == "__main__":
    main()
