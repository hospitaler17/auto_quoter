import requests
from bs4 import BeautifulSoup


class QuoteParser:
    """Парсер страницы цитат.

    Пример использования:
        p = QuoteParser(url, quote_selector, source_selector, source_attr)
        res = p.fetch_all()
        print(res[0]['quote'], res[0]['source'])
    """

    def __init__(
        self,
        url,
        quote_selector,
        source_selector=None,
        source_attr='data-source',
        block_selector=None,
        timeout=10,
    ):
        self.url = url
        self.quote_selector = quote_selector
        self.source_selector = source_selector
        self.source_attr = source_attr
        self.block_selector = block_selector
        self.timeout = timeout

    def _get_soup(self):
        if not self.url:
            raise ValueError("URL не указан")
        resp = requests.get(self.url, timeout=self.timeout)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, 'html.parser')

    def _extract_quote(self, node):
        if not self.quote_selector:
            return None
        q_el = node.select_one(self.quote_selector)
        if not q_el:
            return None
        return " ".join(q_el.get_text(" ", strip=True).split())

    def _extract_source(self, node):
        if not self.source_selector:
            return None
        s_el = node.select_one(self.source_selector)
        if not s_el or not self.source_attr:
            return None
        source = s_el.get(self.source_attr)
        return source.strip() if source else None

    def fetch_all(self):
        """Возвращает список словарей с ключами 'quote' и 'source'."""

        soup = self._get_soup()

        blocks = soup.select(self.block_selector) if self.block_selector else [soup]
        results = []

        for block in blocks:
            quote = self._extract_quote(block)
            if not quote:
                continue
            source = self._extract_source(block)
            results.append({"quote": quote, "source": source})

        return results

    def fetch(self):
        """Совместимость: возвращает первую найденную цитату."""

        results = self.fetch_all()
        if results:
            return results[0]
        return {"quote": None, "source": None}


def get_quote_and_source(url, quote_selector, source_selector=None, source_attr='data-source', timeout=10):
    """Совместимая функция-обёртка, использует `QuoteParser`."""
    parser = QuoteParser(
        url,
        quote_selector,
        source_selector,
        source_attr,
        timeout=timeout,
    )
    return parser.fetch()


def get_string_from_site(url, target_selector, timeout=10):
    """Простой совместимый wrapper — возвращает только текст первого селектора."""
    res = get_quote_and_source(url, target_selector, None, None, timeout=timeout)
    return res.get('quote')
