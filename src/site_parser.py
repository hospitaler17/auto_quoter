import requests
from bs4 import BeautifulSoup


def get_quote_and_source(url, quote_selector, source_selector=None, source_attr='data-source', timeout=10):
    """
    Загружает страницу по `url` и извлекает цитату и источник.

    Возвращает dict: { 'quote': str|None, 'source': str|None }
    """
    if not url:
        raise ValueError("URL не указан")

    response = requests.get(url, timeout=timeout)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    # Извлекаем цитату
    quote = None
    if quote_selector:
        q_el = soup.select_one(quote_selector)
        if q_el:
            # Нормализуем пробелы и non-breaking spaces
            quote = " ".join(q_el.get_text(" ", strip=True).split())

    # Извлекаем источник (атрибут у элемента), если задан селектор
    source = None
    if source_selector:
        s_el = soup.select_one(source_selector)
        if s_el and source_attr:
            source = s_el.get(source_attr)
            if source:
                source = source.strip()

    return {"quote": quote, "source": source}


def get_string_from_site(url, target_selector, timeout=10):
    """Простой совместимый wrapper — возвращает только текст первого селектора."""
    res = get_quote_and_source(url, target_selector, None, None, timeout=timeout)
    return res.get('quote')
