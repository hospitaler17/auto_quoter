import pytest
from unittest.mock import Mock, patch

from src import site_parser


HTML_SNIPPET = '''
<div class="field-name-body">
          <a href="https://citaty.info/quote/256679" class="citaty_info-quote alink" target="_blank"><p>Сочинять, значит быть одиноким до&nbsp;тошноты...</p></a>
</div>
<div class="actions">
  <a class="action copy-to-clipboard" data-source="📚 Дэвид Митчелл, Дэвид Митчелл. Облачный атлас"><span class="action__label">Скопировать</span></a>
</div>
'''


def make_response(text):
    mock = Mock()
    mock.text = text
    mock.status_code = 200
    mock.raise_for_status = Mock()
    return mock


def test_get_quote_and_source_with_source():
    with patch('src.site_parser.requests.get') as mock_get:
        mock_get.return_value = make_response(HTML_SNIPPET)
        # Тестируем класс
        parser = site_parser.QuoteParser(
            'https://citaty.info/random',
            'div.field-name-body a > p',
            'a.copy-to-clipboard',
            'data-source'
        )
        res = parser.fetch()

        assert res['quote'] == 'Сочинять, значит быть одиноким до тошноты...'
        assert res['source'] == '📚 Дэвид Митчелл, Дэвид Митчелл. Облачный атлас'


def test_get_quote_and_source_no_source_selector():
    with patch('src.site_parser.requests.get') as mock_get:
        mock_get.return_value = make_response(HTML_SNIPPET)
        parser = site_parser.QuoteParser(
            'https://citaty.info/random',
            'div.field-name-body a > p',
            None,
            'data-source'
        )
        res = parser.fetch()

        assert res['quote'] == 'Сочинять, значит быть одиноким до тошноты...'
        assert res['source'] is None
