import json
import requests
from bs4 import BeautifulSoup

def test_selectors(url, selectors, timeout=10):
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    results = {}
    for s in selectors:
        el = soup.select_one(s)
        results[s] = el.get_text(" ", strip=True) if el else None

    return results


if __name__ == '__main__':
    with open('config.json', 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    url = cfg.get('url')
    quote_sel = cfg.get('quote_selector')
    source_sel = cfg.get('source_selector')

    selectors = [x for x in [quote_sel, source_sel] if x]
    print('Testing selectors on', url)
    res = test_selectors(url, selectors)
    for s, v in res.items():
        print(f"{s} ->", v)
