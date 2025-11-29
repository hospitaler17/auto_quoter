import json

try:  # pragma: no cover - вспомогательный скрипт
    from .site_parser import QuoteParser
except ImportError:  # pragma: no cover
    from site_parser import QuoteParser


def test_selectors(parser_cfg, timeout=10):
    parser = QuoteParser(
        parser_cfg.get('url'),
        parser_cfg.get('quote_selector'),
        parser_cfg.get('source_selector'),
        parser_cfg.get('source_attr', 'data-source'),
        parser_cfg.get('block_selector'),
        timeout=timeout,
    )
    return parser.fetch_all()


if __name__ == '__main__':
    with open('config.json', 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    parser_cfg = cfg.get('parser') or {}

    print('Testing selectors on', parser_cfg.get('url'))
    entries = test_selectors(parser_cfg, timeout=cfg.get('timeout', 10))
    for idx, entry in enumerate(entries, start=1):
        quote = entry.get('quote') or '<нет цитаты>'
        source = entry.get('source') or '<нет источника>'
        print(f"{idx}. {quote} — {source}")
