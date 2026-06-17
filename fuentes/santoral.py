from datetime import datetime, timedelta


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


def obtener_santoral_semana(fecha_iso):
    fecha = datetime.strptime(fecha_iso, "%Y-%m-%d").date()
    santos = []
    # Spanish day names mapping
    dias_semana = {
        "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
        "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
    }
    for offset in range(0, 7):
        dia = fecha + timedelta(days=offset)
        key = dia.strftime("%m-%d")
        nombre_dia_eng = dia.strftime("%A")
        nombre_dia_esp = dias_semana.get(nombre_dia_eng, nombre_dia_eng)
        santos.append({
            "fecha": f"{nombre_dia_esp} {dia.strftime('%d/%m')}",
            "santo": SANTORAL_MANUAL.get(key, "Santoral pendiente de revisar"),
        })
    return santos

