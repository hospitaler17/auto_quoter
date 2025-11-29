# auto_quoter

Небольшая утилита на Python, которая:

1. Парсит случайную цитату с `https://citaty.info/random` (или любого другого сайта, который вы укажете).
2. Отправляет её в ваш GitHub‑статус через GraphQL API в формате `"<цитата>" — <источник>`.

## Требования

- Python 3.12+
- Персональный GitHub‑токен с правом `user` (нужен для `changeUserStatus`).

## Установка

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```

## Конфигурация (`config.json`)

```json
{
	"url": "https://citaty.info/random",
	"quote_selector": "div.field-name-body a > p",
	"source_selector": "a.copy-to-clipboard",
	"source_attr": "data-source",
	"timeout": 10,
	"github": {
		"enabled": true,
		"token": "YOUR_GITHUB_TOKEN",
		"emoji": ":speech_balloon:",
		"graphql_url": "https://api.github.com/graphql",
		"max_status_length": 80,
		"refresh_interval_seconds": 3600,
		"dry_run": true,
		"debug": false
	}
}
```

- `github.enabled` — включает/выключает отправку статуса без изменения других настроек.
- `github.token` — персональный токен (не публикуйте его). При пустом токене укажите `dry_run: true`, чтобы тестировать без GitHub.
- `github.emoji` — эмодзи рядом со статусом (опционально).
- `github.graphql_url` — альтернативная точка GraphQL (обычно не нужна).
- `github.max_status_length` — максимальная длина строки статуса (по умолчанию 80 символов, как на GitHub).
- `github.refresh_interval_seconds` — через сколько секунд получать новую цитату и продлевать статус. Если `<= 0`, скрипт выполнится один раз.
- `github.dry_run` — при `true` выводит тело GraphQL‑мутации вместо реального запроса.
- `github.debug` — включает подробные логи с запросами и ответами GitHub.

Статус в GitHub получает срок жизни, равный `refresh_interval_seconds`. Пока скрипт активен, он будет обновлять цитату перед истечением статуса.

## Использование

Однократный запуск либо фоновая работа (в зависимости от `refresh_interval_seconds`):

```bash
./scripts/run.sh
```

Подбор CSS‑селекторов (загружает страницу один раз и выводит текст соответствующих элементов):

```bash
python src/parser/selectors_tool.py
```

## Тесты

```bash
./scripts/test.sh
```

Юнит‑тесты подменяют сетевые вызовы (и парсер, и GitHub‑клиент), поэтому их можно запускать офлайн.