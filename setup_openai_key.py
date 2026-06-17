from getpass import getpass
from pathlib import Path


def main():
    print("Configuracion local de OpenAI para Generador Assumpta")
    print("La clave se guardara solo en este ordenador, en el archivo .env")
    api_key = getpass("Pega tu OPENAI_API_KEY y pulsa Enter: ").strip()
    if not api_key:
        print("No se guardo nada: clave vacia.")
        return
    env_path = Path(__file__).with_name(".env")
    env_path.write_text(f"OPENAI_API_KEY={api_key}\n", encoding="utf-8")
    print(f"Clave guardada en {env_path}")
    print("Ya puedes arrancar la app con: python3 app.py")


if __name__ == "__main__":
    main()
