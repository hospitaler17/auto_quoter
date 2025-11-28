import json
import sys
from src.site_parser import QuoteParser


def load_config(config_path='config.json'):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Ошибка: Файл конфигурации '{config_path}' не найден.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Ошибка: Неверный формат JSON в '{config_path}'.")
        sys.exit(1)


if __name__ == "__main__":
    config = load_config()

    url = config.get('url')
    quote_selector = config.get('quote_selector')
    source_selector = config.get('source_selector')
    source_attr = config.get('source_attr', 'data-source')
    timeout = config.get('timeout', 10)

    try:
        parser = QuoteParser(url, quote_selector, source_selector, source_attr, timeout=timeout)
        res = parser.fetch()
    except Exception as e:
        print(f"Ошибка при получении страницы: {e}")
        sys.exit(1)

    quote = res.get('quote')
    source = res.get('source')

    if quote:
        print(f"QUOTE: {quote}")
    else:
        print("QUOTE: не найдено")

    if source:
        print(f"SOURCE: {source}")
    else:
        print("SOURCE: не найдено")
