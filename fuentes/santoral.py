import json
from datetime import datetime, timedelta
from fuentes.ia import generar_texto_ia

SANTORAL_MANUAL = {
    "06-11": "San Bernabe, apostol",
    "06-13": "San Antonio de Padua",
    "06-14": "San Eliseo, profeta; Santos Anastasio, Felix y Digna, mártires",
    "06-15": "Santa Micaela del Santísimo Sacramento; San Bernardo de Menthon",
    "06-16": "San Aureliano, obispo",
    "06-17": "San Gregorio Barbarigo; San Ismael, mártir",
    "06-18": "Santa Isabel de Schönau; San Ciriaco, mártir",
    "06-19": "San Romualdo, abad; San Gervasio, mártir",
    "06-20": "Santa Florentina; San Silverio, papa y mártir",
}


def obtener_santoral_semana(fecha_iso, config=None):
    fecha = datetime.strptime(fecha_iso, "%Y-%m-%d").date()
    santos = []
    # Spanish day names mapping
    dias_semana = {
        "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
        "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
    }
    
    faltan_dias = []
    for offset in range(0, 7):
        dia = fecha + timedelta(days=offset)
        key = dia.strftime("%m-%d")
        nombre_dia_eng = dia.strftime("%A")
        nombre_dia_esp = dias_semana.get(nombre_dia_eng, nombre_dia_eng)
        
        santo = SANTORAL_MANUAL.get(key)
        if not santo:
            faltan_dias.append(dia)
            santo = "Buscando..."
            
        santos.append({
            "fecha": f"{nombre_dia_esp} {dia.strftime('%d/%m')}",
            "santo": santo,
            "_date": dia,
        })
        
    if faltan_dias and config:
        fechas_str = ", ".join([d.strftime("%d/%m") for d in faltan_dias])
        prompt = (
            f"Dime únicamente los nombres de los santos católicos principales que se celebran en España "
            f"en estas fechas (DD/MM): {fechas_str}. "
            "Devuelve la respuesta estrictamente en formato JSON como un diccionario donde la clave sea la fecha en formato 'DD/MM' "
            "y el valor sea el nombre del santo (por ejemplo: {\\\"22/06\\\": \\\"Santo Tomás Moro\\\"}). "
            "No añadas markdown, explicaciones ni ningún otro texto adicional."
        )
        respuesta_ia = generar_texto_ia(config, prompt, fallback="{}")
        try:
            if respuesta_ia.startswith("```json"):
                respuesta_ia = respuesta_ia.replace("```json", "").replace("```", "").strip()
            elif respuesta_ia.startswith("```"):
                respuesta_ia = respuesta_ia.replace("```", "").strip()
                
            santos_ia = json.loads(respuesta_ia)
            for item in santos:
                if item["santo"] == "Buscando...":
                    dia_str = item["_date"].strftime("%d/%m")
                    item["santo"] = santos_ia.get(dia_str, "Santoral pendiente de revisar")
        except Exception as e:
            for item in santos:
                if item["santo"] == "Buscando...":
                    item["santo"] = "Santoral pendiente de revisar"

    for item in santos:
        if "_date" in item:
            del item["_date"]
            
    return santos

