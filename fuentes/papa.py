import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


def _texto_limpio(value):
    return re.sub(r"\s+", " ", value or "").strip()


def obtener_habla_el_papa(index_url):
    """Devuelve un extracto reciente de Vatican.va. Si falla, devuelve texto editable."""
    try:
        response = requests.get(index_url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            text = _texto_limpio(a.get_text(" "))
            href = a["href"]
            if text and ("/speeches/" in href or "/angelus/" in href or "/homilies/" in href):
                links.append((text, urljoin(index_url, href)))
        if not links:
            return {
                "titulo": "Habla el Papa",
                "url": index_url,
                "extracto": "Pendiente de seleccionar extracto reciente del Papa.",
            }
        title, url = links[0]
        article = requests.get(url, timeout=15)
        article.raise_for_status()
        article_soup = BeautifulSoup(article.text, "html.parser")
        paragraphs = [_texto_limpio(p.get_text(" ")) for p in article_soup.find_all("p")]
        paragraphs = [p for p in paragraphs if len(p) > 120]
        return {
            "titulo": title,
            "url": url,
            "extracto": paragraphs[0] if paragraphs else "Pendiente de seleccionar extracto reciente del Papa.",
        }
    except Exception as exc:
        return {
            "titulo": "Habla el Papa",
            "url": index_url,
            "extracto": f"Pendiente de revisar manualmente. No se pudo consultar Vatican.va: {exc}",
        }
