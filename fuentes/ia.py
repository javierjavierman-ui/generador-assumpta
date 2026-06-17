import os

import requests


SYSTEM_PROMPT = "Eres un redactor catolico parroquial. Escribe en espanol sobrio, claro y pastoral."


def _load_local_env():
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    if not os.path.exists(env_path):
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def _chat_completion(base_url, api_key, model, prompt, fallback):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }
    try:
        response = requests.post(base_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return fallback


def generar_texto_openai(config, prompt, fallback):
    _load_local_env()
    openai_config = config.get("openai", {})
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    base_url = openai_config.get("base_url", "https://api.openai.com/v1/chat/completions").strip()
    model = openai_config.get("model", "gpt-4o-mini").strip()

    if not api_key:
        return fallback

    return _chat_completion(base_url, api_key, model, prompt, fallback)


def generar_texto_minimax(config, prompt, fallback):
    """Llama a Minimax si esta configurado; si no, devuelve el fallback local.

    El formato exacto de Minimax puede variar segun el plan/endpoint. Esta funcion
    admite endpoints compatibles con el esquema tipo OpenAI chat completions.
    """
    minimax = config.get("minimax", {})
    api_key = minimax.get("api_key", "").strip()
    base_url = minimax.get("base_url", "").strip()
    model = minimax.get("model", "").strip() or "MiniMax-Text-01"

    if not api_key or not base_url:
        return fallback

    return _chat_completion(base_url, api_key, model, prompt, fallback)


def generar_texto_ia(config, prompt, fallback):
    provider = config.get("ai_provider", "openai").strip().lower()
    if provider == "openai":
        return generar_texto_openai(config, prompt, fallback)
    if provider in ("minimax", "minimax_free"):
        return generar_texto_minimax(config, prompt, fallback)
    return fallback


def slugify(text):
    import re
    text = text.lower()
    text = re.sub(r'[áàäâ]', 'a', text)
    text = re.sub(r'[éèëê]', 'e', text)
    text = re.sub(r'[íìïî]', 'i', text)
    text = re.sub(r'[óòöô]', 'o', text)
    text = re.sub(r'[úùüû]', 'u', text)
    text = re.sub(r'[ñ]', 'n', text)
    text = re.sub(r'[^a-z0-9_-]', '-', text)
    return re.sub(r'-+', '-', text).strip('-')


def generar_imagen_dalle(santo_nombre):
    _load_local_env()
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None

    filename_slug = slugify(santo_nombre)
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "images"))
    os.makedirs(static_dir, exist_ok=True)
    target_path = os.path.join(static_dir, f"{filename_slug}.png")

    if os.path.exists(target_path):
        return f"static/images/{filename_slug}.png"

    prompt = (
        f"Retrato de {santo_nombre}. Estilo pintura clásica al óleo, "
        "arte sacro católico medieval y renacentista, iluminación dramática tenebrista, "
        "rostro sereno y piadoso, fondo neutro oscuro y difuminado, "
        "estilo realista de museo."
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "dall-e-2",
        "prompt": prompt,
        "n": 1,
        "size": "256x256"
    }

    import urllib.request
    try:
        response = requests.post("https://api.openai.com/v1/images/generations", headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        res_data = response.json()
        img_url = res_data["data"][0]["url"]

        with urllib.request.urlopen(img_url) as response_img:
            with open(target_path, "wb") as out_file:
                out_file.write(response_img.read())

        return f"static/images/{filename_slug}.png"
    except Exception as e:
        print(f"Error generando imagen de {santo_nombre}: {e}")
        return None

