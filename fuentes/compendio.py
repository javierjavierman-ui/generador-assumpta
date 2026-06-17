import os
import re

from pdfminer.high_level import extract_text


def extraer_pregunta_compendio(pdf_path, numero):
    resolved = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", pdf_path))
    if not os.path.exists(resolved):
        return f"{numero}. No se encontro el PDF del Compendio en {resolved}."

    text = extract_text(resolved)
    pattern = rf"(?ms)(^|\n){numero}\.\s+(.+?)(?=\n{numero + 1}\.\s+|\nCAP[IÍ]TULO|\n[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ ]{{8,}}|\Z)"
    match = re.search(pattern, text)
    if not match:
        return f"{numero}. No se encontro esta pregunta en el Compendio."
    return re.sub(r"\n{3,}", "\n\n", f"{numero}. {match.group(2).strip()}").strip()
