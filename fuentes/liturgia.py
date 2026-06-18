"""
Módulo de liturgia dominical.

Fuente principal: Universalis.com (localizacion Spain, en espanol).
URL base: https://universalis.com/spain/YYYYMMDD/mass.htm

Extrae de la pagina HTML:
  - Nombre de la celebracion dominical (feastname)
  - Primera y segunda lectura (referencias)
  - Salmo responsorial
  - Evangelio (referencia + titulo)

Si la conexion falla o la estructura HTML cambia, devuelve un
texto de aviso para que el usuario complete el campo manualmente.
"""

import logging
import re
from datetime import datetime, date, timedelta

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────
# Constantes
# ──────────────────────────────────────────────────────────
UNIVERSALIS_URL = "https://universalis.com/spain/{fecha}/mass.htm"
TIMEOUT_SEGUNDOS = 10
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; Assumpta-Parroquial/1.0; "
        "+https://github.com/local/assumpta)"
    )
}

# Traducciones de términos litúrgicos inglés → español
_TRADUCCIONES_LECTURAS = {
    "First reading": "Primera Lectura",
    "Second reading": "Segunda Lectura",
    "Gospel": "Evangelio",
    "Psalm": "Salmo",
    "Responsorial Psalm": "Salmo Responsorial",
    "Acclamation": "Aclamacion",
    "Alternative first reading": "Primera Lectura (alternativa)",
    "Alternative second reading": "Segunda Lectura (alternativa)",
}

# Traducciones de nombres litúrgicos de temporada (orden importa: más específico primero)
_TRADUCCIONES_CELEBRACION = [
    # ── Domingos numerados del Tiempo Ordinario ──
    # Formato Universalis: "12th Sunday in Ordinary Time"
    (r"(\d+)(?:st|nd|rd|th) Sunday in Ordinary Time",    r"Domingo \1 del Tiempo Ordinario"),
    # Formato alternativo: "Sunday of week N in Ordinary Time"
    (r"Sunday of week (\d+) in Ordinary Time",           r"Domingo \1 del Tiempo Ordinario"),
    # ── Semanas del Tiempo Ordinario (días entre semana) ──
    (r"week (\d+) in Ordinary Time",                     r"Semana \1 del Tiempo Ordinario"),
    # ── Adviento ──
    (r"(\d+)(?:st|nd|rd|th) Sunday of Advent",          r"Domingo \1 de Adviento"),
    # ── Cuaresma ──
    (r"(\d+)(?:st|nd|rd|th) Sunday of Lent",            r"Domingo \1 de Cuaresma"),
    # ── Semana Santa ──
    (r"Palm Sunday",     "Domingo de Ramos"),
    (r"Good Friday",     "Viernes Santo"),
    (r"Holy Saturday",   "Sábado Santo"),
    # ── Pascua ──
    (r"Easter Sunday",   "Domingo de Pascua de Resurrección"),
    (r"(\d+)(?:st|nd|rd|th) Sunday of Easter", r"Domingo \1 de Pascua"),
    # ── Tiempo Pascual ──
    (r"Pentecost Sunday",                          "Domingo de Pentecostés"),
    # ── Solemnidades fijas ──
    (r"Trinity Sunday",                            "Solemnidad de la Santísima Trinidad"),
    (r"The Most Holy Body and Blood of Christ",    "Corpus Christi"),
    (r"Christ the King",                           "Solemnidad de Cristo Rey"),
    (r"The Immaculate Conception of the Blessed Virgin Mary",
                                                   "Inmaculada Concepción de la Santísima Virgen María"),
    (r"The Assumption of the Blessed Virgin Mary", "Asunción de la Santísima Virgen María"),
    (r"All Saints",       "Solemnidad de Todos los Santos"),
    (r"All Souls",        "Conmemoración de los Fieles Difuntos"),
    (r"The Nativity of the Lord",   "La Natividad del Señor (Navidad)"),
    (r"The Epiphany of the Lord",   "La Epifanía del Señor"),
    (r"The Baptism of the Lord",    "El Bautismo del Señor"),
    (r"The Holy Family",            "La Sagrada Familia"),
    (r"Ash Wednesday",              "Miércoles de Ceniza"),
    # ── Días de la semana (cuando aparecen solos) ──
    (r"\bMonday\b",    "Lunes"),
    (r"\bTuesday\b",   "Martes"),
    (r"\bWednesday\b", "Miércoles"),
    (r"\bThursday\b",  "Jueves"),
    (r"\bFriday\b",    "Viernes"),
    (r"\bSaturday\b",  "Sábado"),
    (r"\bSunday\b",    "Domingo"),
    # ── Limpieza de preposiciones residuales en inglés ──
    (r"\bof\b",  "de"),
    (r"\bin\b",  "del"),
]

# Traducción de referencias bíblicas (abreviaturas comunes inglés→español)
_TRADUCCIONES_LIBROS = {
    "Genesis": "Génesis", "Gen": "Gén",
    "Exodus": "Éxodo", "Exod": "Ex",
    "Leviticus": "Levítico", "Lev": "Lev",
    "Numbers": "Números", "Num": "Núm",
    "Deuteronomy": "Deuteronomio", "Deut": "Dt",
    "Joshua": "Josué",
    "Judges": "Jueces",
    "Ruth": "Rut",
    "1 Samuel": "1 Samuel", "2 Samuel": "2 Samuel",
    "1 Kings": "1 Reyes", "2 Kings": "2 Reyes",
    "1 Chronicles": "1 Crónicas", "2 Chronicles": "2 Crónicas",
    "Ezra": "Esdras",
    "Nehemiah": "Nehemías",
    "Tobit": "Tobías",
    "Judith": "Judit",
    "Esther": "Ester",
    "1 Maccabees": "1 Macabeos", "2 Maccabees": "2 Macabeos",
    "Job": "Job",
    "Psalms": "Salmos", "Psalm": "Salmo",
    "Proverbs": "Proverbios",
    "Ecclesiastes": "Eclesiastés",
    "Song of Solomon": "Cantar de los Cantares",
    "Wisdom": "Sabiduría",
    "Sirach": "Eclesiástico",
    "Isaiah": "Isaías",
    "Jeremiah": "Jeremías",
    "Lamentations": "Lamentaciones",
    "Baruch": "Baruc",
    "Ezekiel": "Ezequiel",
    "Daniel": "Daniel",
    "Hosea": "Oseas",
    "Joel": "Joel",
    "Amos": "Amós",
    "Obadiah": "Abdías",
    "Jonah": "Jonás",
    "Micah": "Miqueas",
    "Nahum": "Nahún",
    "Habakkuk": "Habacuc",
    "Zephaniah": "Sofonías",
    "Haggai": "Ageo",
    "Zechariah": "Zacarías",
    "Malachi": "Malaquías",
    "Matthew": "Mateo", "Matt": "Mt",
    "Mark": "Marcos", "Mk": "Mc",
    "Luke": "Lucas", "Lk": "Lc",
    "John": "Juan", "Jn": "Jn",
    "Acts": "Hechos",
    "Romans": "Romanos", "Rom": "Rom",
    "1 Corinthians": "1 Corintios", "2 Corinthians": "2 Corintios",
    "Galatians": "Gálatas",
    "Ephesians": "Efesios",
    "Philippians": "Filipenses",
    "Colossians": "Colosenses",
    "1 Thessalonians": "1 Tesalonicenses", "2 Thessalonians": "2 Tesalonicenses",
    "1 Timothy": "1 Timoteo", "2 Timothy": "2 Timoteo",
    "Titus": "Tito",
    "Philemon": "Filemón",
    "Hebrews": "Hebreos",
    "James": "Santiago",
    "1 Peter": "1 Pedro", "2 Peter": "2 Pedro",
    "1 John": "1 Juan", "2 John": "2 Juan", "3 John": "3 Juan",
    "Jude": "Judas",
    "Revelation": "Apocalipsis",
}


# ──────────────────────────────────────────────────────────
# Funciones auxiliares
# ──────────────────────────────────────────────────────────

def _traducir_celebracion(texto_ingles: str) -> str:
    """Aplica traducciones al nombre de la celebración."""
    resultado = texto_ingles.strip()
    for patron, reemplazo in _TRADUCCIONES_CELEBRACION:
        resultado = re.sub(patron, reemplazo, resultado, flags=re.IGNORECASE)
    return resultado


def _traducir_referencia(referencia: str) -> str:
    """Traduce el nombre del libro bíblico al español."""
    resultado = referencia.strip()
    for ingles, espanol in _TRADUCCIONES_LIBROS.items():
        resultado = re.sub(r'\b' + re.escape(ingles) + r'\b', espanol, resultado)
    return resultado


def _extraer_datos_universalis(soup: BeautifulSoup) -> dict:
    """
    Extrae celebración, lecturas, salmo y evangelio del HTML de Universalis.
    Devuelve None si no puede extraer datos mínimos.
    """
    datos = {
        "celebracion": None,
        "lecturas": [],
        "salmo": None,
        "evangelio": None,
    }

    # 1. Nombre de la celebración: <span id="feastname"><strong>...
    feast = soup.find(id="feastname")
    if feast:
        # Tomar solo el texto del <strong> para evitar contenido de subelementos extra
        strong = feast.find("strong")
        texto_raw = (strong.get_text(strip=True) if strong
                     else feast.get_text(strip=True))
        datos["celebracion"] = _traducir_celebracion(texto_raw)

    # 2. Lecturas: buscar <table class="each"> con <th> que indiquen tipo
    tablas = soup.find_all("table", class_="each")
    for tabla in tablas:
        encabezados = tabla.find_all("th")
        if len(encabezados) < 1:
            continue
        tipo_ing = encabezados[0].get_text(strip=True)  # "First reading", "Gospel"…
        referencia = encabezados[1].get_text(strip=True) if len(encabezados) > 1 else ""
        tipo_esp = _TRADUCCIONES_LECTURAS.get(tipo_ing, tipo_ing)
        ref_esp = _traducir_referencia(referencia)

        if "Psalm" in tipo_ing or "psalm" in tipo_ing.lower():
            datos["salmo"] = ref_esp
        elif "Gospel" in tipo_ing:
            datos["evangelio"] = f"{ref_esp}"
        elif "reading" in tipo_ing.lower():
            datos["lecturas"].append(f"{tipo_esp}: {ref_esp}")
        # ignorar aclamaciones y otros

    return datos


def _fallback(motivo: str = "") -> dict:
    """Devuelve un diccionario de reserva claro para el usuario."""
    aviso = (
        "[Liturgia no disponible automáticamente"
        + (f" — {motivo}" if motivo else "")
        + ". Por favor, completa este campo manualmente.]"
    )
    return {
        "celebracion": aviso,
        "lecturas": aviso,
        "salmo": aviso,
        "evangelio": aviso,
    }


# ──────────────────────────────────────────────────────────
# Función pública
# ──────────────────────────────────────────────────────────

def obtener_liturgia(fecha_iso: str) -> dict:
    """
    Devuelve un diccionario con los datos litúrgicos del domingo indicado.

    Campos devueltos:
      - celebracion (str): Nombre del domingo/celebración.
      - lecturas    (str): Referencias de la primera y segunda lectura.
      - salmo       (str): Referencia del salmo responsorial.
      - evangelio   (str): Referencia del evangelio.

    Fuente: Universalis.com (Spain locale).
    Si hay cualquier error de red o parsing, devuelve texto de aviso.
    """
    try:
        # Convertir fecha al formato YYYYMMDD que usa Universalis
        dt = datetime.strptime(fecha_iso, "%Y-%m-%d")
        
        # Asegurarnos de que sea domingo (weekday() == 6)
        if dt.weekday() != 6:
            dias_hasta_domingo = 6 - dt.weekday()
            dt = dt + timedelta(days=dias_hasta_domingo)
            logger.info("Fecha ajustada al domingo: %s", dt)
            
        fecha_uni = dt.strftime("%Y%m%d")
        url = UNIVERSALIS_URL.format(fecha=fecha_uni)

        logger.info("Consultando liturgia en: %s", url)
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SEGUNDOS)
        resp.raise_for_status()
        resp.encoding = "utf-8"

        soup = BeautifulSoup(resp.text, "html.parser")
        datos = _extraer_datos_universalis(soup)

        # Validar que tenemos al menos la celebración
        if not datos["celebracion"]:
            logger.warning("No se encontro el nombre de la celebracion en Universalis.")
            return _fallback("no se encontró la celebración en la fuente")

        # Formatear lecturas como cadena
        lecturas_str = (
            " / ".join(datos["lecturas"])
            if datos["lecturas"]
            else "[Lecturas no detectadas — revisar manualmente]"
        )

        return {
            "celebracion": datos["celebracion"],
            "lecturas": lecturas_str,
            "salmo": datos["salmo"] or "[Salmo no detectado — revisar manualmente]",
            "evangelio": datos["evangelio"] or "[Evangelio no detectado — revisar manualmente]",
            "fuente": url,
        }

    except requests.exceptions.ConnectionError:
        logger.error("Sin conexion a internet al consultar Universalis.")
        return _fallback("sin conexión a internet")
    except requests.exceptions.Timeout:
        logger.error("Tiempo de espera agotado consultando Universalis.")
        return _fallback("tiempo de espera agotado")
    except requests.exceptions.HTTPError as exc:
        logger.error("Error HTTP al consultar Universalis: %s", exc)
        return _fallback(f"error HTTP {exc.response.status_code}")
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Error inesperado en obtener_liturgia: %s", exc)
        return _fallback(str(exc))
