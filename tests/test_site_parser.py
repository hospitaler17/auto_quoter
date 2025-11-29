import pytest
from unittest.mock import Mock, patch

from src.parser import site_parser


HTML_SNIPPET = '''
<article class="node node-quote">
    <div class="field-name-body">
        <a href="https://citaty.info/quote/256679" class="citaty_info-quote alink" target="_blank">
            <p>Сочинять, значит быть одиноким до&nbsp;тошноты...</p>
        </a>
    </div>
    <div class="actions">
        <a class="action copy-to-clipboard" data-source="📚 Дэвид Митчелл, Облачный атлас"><span class="action__label">Скопировать</span></a>
    </div>
</article>
<article class="node node-quote">
    <div class="field-name-body">
        <a href="https://citaty.info/quote/129940" class="citaty_info-quote alink" target="_blank">
            <p>Денег, которые я&nbsp;заработал, хватит мне&nbsp;до&nbsp;конца жизни...</p>
        </a>
    </div>
    <div class="actions">
        <a class="action copy-to-clipboard" data-source="🧑🏼 Хенни Янгман"><span class="action__label">Скопировать</span></a>
    </div>
</article>
'''


def make_response(text):
    mock = Mock()
    mock.text = text
    mock.status_code = 200
    mock.raise_for_status = Mock()
    return mock


def test_fetch_all_returns_multiple_quotes():
    with patch('src.parser.site_parser.requests.get') as mock_get:
        mock_get.return_value = make_response(HTML_SNIPPET)
        parser = site_parser.QuoteParser(
            'https://citaty.info/short',
            'div.field-name-body a > p',
            'a.copy-to-clipboard',
            'data-source',
            'article.node-quote'
        )
        results = parser.fetch_all()

        assert len(results) == 2
        assert results[0]['quote'] == 'Сочинять, значит быть одиноким до тошноты...'
        assert results[0]['source'] == '📚 Дэвид Митчелл, Облачный атлас'
        assert results[1]['quote'].startswith('Денег, которые я заработал')
        assert results[1]['source'] == '🧑🏼 Хенни Янгман'


def test_fetch_all_without_source_selector_returns_none_sources():
    with patch('src.parser.site_parser.requests.get') as mock_get:
        mock_get.return_value = make_response(HTML_SNIPPET)
        parser = site_parser.QuoteParser(
            'https://citaty.info/short',
            'div.field-name-body a > p',
            None,
            'data-source',
            'article.node-quote'
        )
        results = parser.fetch_all()

        assert len(results) == 2
        assert all(item['source'] is None for item in results)


def test_fetch_returns_first_entry():
    with patch('src.parser.site_parser.requests.get') as mock_get:
        mock_get.return_value = make_response(HTML_SNIPPET)
        parser = site_parser.QuoteParser(
            'https://citaty.info/short',
            'div.field-name-body a > p',
            'a.copy-to-clipboard',
            'data-source',
            'article.node-quote'
        )

        result = parser.fetch()

        assert result['quote'] == 'Сочинять, значит быть одиноким до тошноты...'
        assert result['source'] == '📚 Дэвид Митчелл, Облачный атлас'
