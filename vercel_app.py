from __future__ import annotations

import base64
import cgi
import io
import os
import tempfile
from contextlib import redirect_stdout
from urllib.parse import parse_qs

from flask import Flask, Response, request, send_file

import app as local_app

app = Flask(__name__)


class _CaptureHandler(local_app.Handler):
    def __init__(self, method="GET", path="/"):
        self.command = method
        self.path = path
        self.headers = {}
        self.status = 200
        self.response_headers = []
        self.wfile = io.BytesIO()

    def send_response(self, status):
        self.status = status

    def send_header(self, name, value):
        self.response_headers.append((name, value))

    def end_headers(self):
        pass

    def send_error(self, status):
        self.status = status
        self.wfile.write(f"Error {status}".encode("utf-8"))

    def render_share_box(self):
        return "<section class='notice'><strong>Version web.</strong> Esta version esta publicada en Vercel. Para produccion final, revise siempre la previsualizacion y el PDF generado.</section>"


def _authorized() -> bool:
    header = request.headers.get("Authorization", "")
    if not header.startswith("Basic "):
        return False
    try:
        decoded = base64.b64decode(header.split(" ", 1)[1]).decode("utf-8")
    except Exception:
        return False
    return decoded == f"{local_app.AUTH_USERNAME}:{local_app.AUTH_PASSWORD}"


def _auth_required():
    return Response(
        "Acceso protegido al Generador Assumpta.",
        401,
        {"WWW-Authenticate": 'Basic realm="Generador Assumpta"'},
    )


def _response_from_handler(handler: _CaptureHandler) -> Response:
    body = handler.wfile.getvalue()
    headers = {k: v for k, v in handler.response_headers if k.lower() != "content-length"}
    return Response(body, status=handler.status, headers=headers)


@app.route("/", methods=["GET", "POST"])
def index():
    if not _authorized():
        return _auth_required()
    if request.method == "GET":
        handler = _CaptureHandler("GET", request.full_path)
        query = parse_qs(request.query_string.decode("utf-8", errors="ignore"))
        fecha = query.get("fecha", [""])[0]
        handler.render_form(data={"fecha": fecha} if fecha else None)
        return _response_from_handler(handler)

    import assumpta_core
    tmpdir = tempfile.gettempdir()
    assumpta_core.OUTPUT_DIR = os.path.join(tmpdir, "output")
    assumpta_core.PREVIEW_DIR = os.path.join(tmpdir, "previews")
    assumpta_core.ASSET_DIR = os.path.join(tmpdir, "assets")
    assumpta_core.LITURGY_SOURCE_DIR = os.path.join(tmpdir, "liturgy_sources")
    local_app.UPLOAD_DIR = os.path.join(tmpdir, "uploads")
    os.makedirs(assumpta_core.OUTPUT_DIR, exist_ok=True)
    os.makedirs(assumpta_core.PREVIEW_DIR, exist_ok=True)
    os.makedirs(assumpta_core.ASSET_DIR, exist_ok=True)
    os.makedirs(assumpta_core.LITURGY_SOURCE_DIR, exist_ok=True)
    os.makedirs(local_app.UPLOAD_DIR, exist_ok=True)
    form = cgi.FieldStorage(fp=io.BytesIO(request.get_data()), headers=dict(request.headers), environ={
            "REQUEST_METHOD": "POST",
            "CONTENT_TYPE": request.headers.get("Content-Type", ""),
            "CONTENT_LENGTH": request.headers.get("Content-Length", "0"),
    })
    handler = _CaptureHandler("POST", request.full_path)
    action = local_app.read_field(form, "action", "proof")
    proof = action != "production"
    result, data, next_question = handler.build_result_from_form(form, proof=proof)
    if result.get("pdf") and os.path.exists(result["pdf"]):
        return send_file(
            result["pdf"],
            mimetype="application/pdf",
            as_attachment=False,
            download_name=os.path.basename(result["pdf"]),
        )
    handler.render_form(result=result, data=data, next_question=next_question)
    return _response_from_handler(handler)


@app.route("/static/<path:name>")
def static_files(name):
    if not _authorized():
        return _auth_required()
    if name.startswith("previews/"):
        tmp_preview = os.path.join(tempfile.gettempdir(), "previews", os.path.basename(name))
        if os.path.exists(tmp_preview):
            return send_file(tmp_preview)
    path = os.path.join(local_app.BASE_DIR, "static", name)
    if os.path.exists(path):
        return send_file(path)
    return Response("Not found", 404)


@app.route("/output/<path:name>")
def output_files(name):
    if not _authorized():
        return _auth_required()
    tmp_output = os.path.join(tempfile.gettempdir(), "output", os.path.basename(name))
    if os.path.exists(tmp_output):
        return send_file(tmp_output)
    path = os.path.join(local_app.BASE_DIR, "output", name)
    if os.path.exists(path):
        return send_file(path)
    return Response("El PDF se ha generado en una sesion temporal. Vuelva a generarlo y abra el enlace inmediatamente.", 404)
