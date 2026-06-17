# Generador Assumpta

App web local para preparar la hoja parroquial Assumpta.

## Arranque

```bash
cd /Users/javiermanuelrodriguezrodriguez/Desktop/Assumpta/generador_assumpta
python3 -m pip install -r requirements.txt
python3 app.py
```

Abrir: http://127.0.0.1:5000

## IA: OpenAI o Minimax

La app funciona aunque no haya proveedor de IA configurado: genera borradores locales editables.

El proveedor se elige en `config.json` con `ai_provider`:

```json
"ai_provider": "openai"
```

o bien:

```json
"ai_provider": "minimax_free"
```

### OpenAI

OpenAI lee la clave desde la variable de entorno `OPENAI_API_KEY` o desde un archivo local `.env`.

Forma sencilla:

```bash
python3 setup_openai_key.py
python3 app.py
```

Forma manual:

```bash
export OPENAI_API_KEY="tu_clave_aqui"
python3 app.py
```

`config.json` permite elegir modelo:

```json
"openai": {
  "model": "gpt-4o-mini",
  "base_url": "https://api.openai.com/v1/chat/completions"
}
```

### Minimax

Para activar Minimax, edita `config.json` y completa:

```json
"minimax": {
  "api_key": "TU_TOKEN_LOCAL",
  "base_url": "ENDPOINT_COMPATIBLE_CHAT_COMPLETIONS",
  "model": "MiniMax-Text-01"
}
```

No pegues claves en chats ni en repositorios publicos.

## Estado

`state.json` guarda:

- `last_assumpta_number`
- `next_compendio_question`

Al pulsar "Generar HTML/Markdown y avanzar estado", la app incrementa ambos valores.
