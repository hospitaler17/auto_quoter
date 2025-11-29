import requests
from bs4 import BeautifulSoup


class QuoteParser:
    """Парсер страницы цитат.

    Пример использования:
        p = QuoteParser(url, quote_selector, source_selector, source_attr)
        res = p.fetch()
        print(res['quote'], res['source'])
    """

    def __init__(self, url, quote_selector, source_selector=None, source_attr='data-source', timeout=10):
        self.url = url
        self.quote_selector = quote_selector
        self.source_selector = source_selector
        self.source_attr = source_attr
        self.timeout = timeout

    def _get_soup(self):
        if not self.url:
            raise ValueError("URL не указан")
        resp = requests.get(self.url, timeout=self.timeout)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, 'html.parser')

    def fetch(self):
        """Возвращает dict с ключами 'quote' и 'source'."""
        soup = self._get_soup()

        quote = None
        if self.quote_selector:
            q_el = soup.select_one(self.quote_selector)
            if q_el:
                quote = " ".join(q_el.get_text(" ", strip=True).split())

        source = None
        if self.source_selector:
            s_el = soup.select_one(self.source_selector)
            if s_el and self.source_attr:
                source = s_el.get(self.source_attr)
                if source:
                    source = source.strip()

        return {"quote": quote, "source": source}


def get_quote_and_source(url, quote_selector, source_selector=None, source_attr='data-source', timeout=10):
    """Совместимая функция-обёртка, использует `QuoteParser`."""
    parser = QuoteParser(url, quote_selector, source_selector, source_attr, timeout=timeout)
    return parser.fetch()


def get_string_from_site(url, target_selector, timeout=10):
    """Простой совместимый wrapper — возвращает только текст первого селектора."""
    res = get_quote_and_source(url, target_selector, None, None, timeout=timeout)
    return res.get('quote')
