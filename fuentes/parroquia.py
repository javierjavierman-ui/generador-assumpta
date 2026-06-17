import feedparser


def obtener_servicio_informativo(feed_url, max_items=6):
    feed = feedparser.parse(feed_url)
    items = []
    for entry in feed.entries[:max_items]:
        items.append({
            "titulo": getattr(entry, "title", "Sin titulo"),
            "url": getattr(entry, "link", ""),
            "fecha": getattr(entry, "published", ""),
        })
    return items
