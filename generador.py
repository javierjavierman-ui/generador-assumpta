import html
import json
import os
from datetime import datetime

from fuentes.compendio import extraer_pregunta_compendio
from fuentes.ia import generar_texto_ia
from fuentes.liturgia import obtener_liturgia
from fuentes.papa import obtener_habla_el_papa
from fuentes.parroquia import obtener_servicio_informativo
from fuentes.santoral import obtener_santoral_semana


BASE_DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
STATE_PATH = os.path.join(BASE_DIR, "state.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def cargar_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def cargar_contexto_base(fecha_iso):
    config = cargar_json(CONFIG_PATH)
    state = cargar_json(STATE_PATH)
    numero_assumpta = state["last_assumpta_number"] + 1
    numero_compendio = state["next_compendio_question"]
    return {
        "config": config,
        "state": state,
        "numero_assumpta": numero_assumpta,
        "numero_compendio": numero_compendio,
        "fecha_iso": fecha_iso,
        "fecha_larga": datetime.strptime(fecha_iso, "%Y-%m-%d").strftime("%d de %m de %Y"),
        "liturgia": obtener_liturgia(fecha_iso),
        "santoral": obtener_santoral_semana(fecha_iso),
        "papa": obtener_habla_el_papa(config["vatican_speeches_url"]),
        "servicio": obtener_servicio_informativo(config["parish_feed_url"]),
        "compendio": extraer_pregunta_compendio(config["compendio_pdf"], numero_compendio),
    }


def generar_carta_borrador(liturgia):
    celebracion = liturgia.get("celebracion") or "el domingo"
    evangelio = liturgia.get("evangelio") or "el Evangelio del domingo"
    return (
        "Queridos feligreses:\n\n"
        f"Celebramos {celebracion}. El Evangelio nos invita a mirar de nuevo a Cristo "
        "como centro de nuestra vida y de nuestra comunidad parroquial. "
        f"A partir de la Palabra proclamada ({evangelio}), podemos preguntarnos como "
        "acoger mejor al Senor en lo ordinario: en la oracion, en la Eucaristia, en la "
        "vida familiar y en la caridad concreta con quienes mas lo necesitan.\n\n"
        "Que esta semana sea ocasion para renovar nuestra fe y vivir con mayor alegria "
        "la pertenencia a la Iglesia.\n\n"
        "Vuestro Parroco"
    )


def generar_carta(config, liturgia):
    fallback = generar_carta_borrador(liturgia)
    prompt = (
        "Redacta una carta breve del parroco para la hoja parroquial Assumpta. "
        "Debe empezar con 'Queridos feligreses:' y terminar con 'Vuestro Parroco'. "
        "Extensión aproximada: 140-180 palabras. Tono cercano, doctrinalmente seguro, "
        "sin lenguaje grandilocuente. Baseala en estos datos liturgicos:\n\n"
        f"Celebracion: {liturgia.get('celebracion')}\n"
        f"Lecturas: {liturgia.get('lecturas')}\n"
        f"Salmo: {liturgia.get('salmo')}\n"
        f"Evangelio: {liturgia.get('evangelio')}"
    )
    return generar_texto_ia(config, prompt, fallback)


def generar_mane_borrador(liturgia):
    celebracion = liturgia.get("celebracion") or "la liturgia dominical"
    return f"Mane nobiscum, Domine. Quedate con nosotros, Senor, y ensenanos a vivir {celebracion} con fe sencilla y caridad concreta."


def generar_mane(config, liturgia):
    fallback = generar_mane_borrador(liturgia)
    prompt = (
        "Genera una frase breve para la seccion 'Mane nobiscum, Domine' de una hoja parroquial. "
        "Debe incluir la expresion latina y una breve aplicacion espiritual de una frase. "
        f"Tema liturgico: {liturgia.get('celebracion')}. Evangelio: {liturgia.get('evangelio')}"
    )
    return generar_texto_ia(config, prompt, fallback)


def render_markdown(data):
    servicio = "\n".join([f"- [{item['titulo']}]({item['url']})" for item in data["servicio"]])
    santoral = "\n".join([f"- {item['fecha']}: {item['santo']}" for item in data["santoral"]])
    return f"""# ASSUMPTA {data['numero_assumpta']}

**Fecha:** {data['fecha_larga']}

## Carta del Parroco

{data['carta']}

## Santoral

{santoral}

## Mane nobiscum, Domine

{data['mane']}

## Vida Parroquial

{data['vida_parroquial'] or 'Pendiente de completar.'}

## Habla el Papa

**{data['papa']['titulo']}**

{data['papa']['extracto']}

Fuente: {data['papa']['url']}

## Nuestro Servicio Informativo

{servicio or 'Sin entradas recientes.'}

## Liturgia Dominical

**Celebracion:** {data['liturgia']['celebracion']}

**Lecturas:** {data['liturgia']['lecturas']}

**Salmo:** {data['liturgia']['salmo']}

**Evangelio:** {data['liturgia']['evangelio']}

## Catecismo de la Iglesia Catolica - Compendio

{data['compendio']}

## Datos Fijos

APERTURA DE LA IGLESIA: 8:30 a 14:00 y 17:00 a 21:00.  
MISAS: Lunes a sabado, 9:00 y 20:00. Domingo, 10:00, 11:00, 12:00, 13:00, 19:00 y 20:00.  
CONFESIONES: Lunes y miercoles, 19:00 a 20:00; resto de dias, media hora antes de cada Misa.  
PARROQUIA ASUNCION DE NUESTRA SENORA, Camino de Valladolid, 26, Torrelodones.
"""


def render_html(markdown_text):
    body = "\n".join(f"<p>{html.escape(line)}</p>" if line else "" for line in markdown_text.splitlines())
    return f"<!doctype html><html lang='es'><head><meta charset='utf-8'><title>Assumpta</title><link rel='stylesheet' href='../static/style.css'></head><body>{body}</body></html>"


def guardar_salida(data, avanzar_estado=False):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    base = f"assumpta-{data['numero_assumpta']}-{data['fecha_iso']}"
    md = render_markdown(data)
    html_text = render_html(md)
    md_path = os.path.join(OUTPUT_DIR, base + ".md")
    html_path = os.path.join(OUTPUT_DIR, base + ".html")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_text)
    if avanzar_estado:
        state = cargar_json(STATE_PATH)
        state["last_assumpta_number"] = data["numero_assumpta"]
        state["next_compendio_question"] = data["numero_compendio"] + 1
        guardar_json(STATE_PATH, state)
    return md_path, html_path
