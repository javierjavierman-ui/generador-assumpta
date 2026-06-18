import os
import re

from pypdf import PdfReader


def extraer_pregunta_compendio(pdf_path, numero, cantidad=4):
    resolved = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", pdf_path))
    if not os.path.exists(resolved):
        return f"{numero}. No se encontro el PDF del Compendio en {resolved}."

    try:
        reader = PdfReader(resolved)
        text = ""
        for page in reader.pages:
            pt = page.extract_text()
            if pt:
                text += pt
    except Exception as e:
        return f"{numero}. Error leyendo el Compendio: {e}"

    resultados = []
    for n in range(numero, numero + cantidad):
        pattern = rf"(?ms)(^|\n){n}\.\s+(.+?)(?=\n{n + 1}\.\s+|\nCAP[IÍ]TULO|\n[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ ]{{8,}}|\Z)"
        match = re.search(pattern, text)
        if match:
            limpio = re.sub(r"\n{3,}", "\n\n", f"{n}. {match.group(2).strip()}").strip()
            # Limpiar saltos de línea molestos dentro del mismo párrafo
            limpio = re.sub(r"(?<!\n)\n(?!\n)", " ", limpio)
            resultados.append(limpio)
        else:
            if n == numero:
                return f"{numero}. No se encontro esta pregunta en el Compendio."
            break

    return "\n\n".join(resultados)

