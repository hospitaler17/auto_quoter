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
	"parser": {
		"url": "https://citaty.info/short",
		"quote_selector": "div.field-name-body a > p",
		"source_selector": "a.copy-to-clipboard",
		"source_attr": "data-source",
		"block_selector": "article.node-quote"
	},
	"timeout": 10,
	"loop": true,
	"refresh_interval_seconds": 3600,
	"debug": false,
	"github": {
		"enabled": true,
		"token": "YOUR_GITHUB_TOKEN",
		"emoji": ":speech_balloon:",
		"graphql_url": "https://api.github.com/graphql",
		"max_status_length": 80,
		"dry_run": true
	}
}
```

- `parser.*` — настройки CSS‑селекторов. `block_selector` задаёт контейнер для каждой цитаты (например, `article.node-quote` на странице `/short`). Внутри блока выполняются `quote_selector` и `source_selector`, так что можно собирать сразу все цитаты со страницы.
- `github.enabled` — включает/выключает отправку статуса без изменения других настроек.
- `github.token` — персональный токен (не публикуйте его). При пустом токене укажите `dry_run: true`, чтобы тестировать без GitHub.
- `github.emoji` — эмодзи рядом со статусом (опционально).
- `github.graphql_url` — альтернативная точка GraphQL (обычно не нужна).
- `loop` — запускает ли скрипт в цикле. Если `false`, выполнится один проход.
- `refresh_interval_seconds` — общий интервал (в секундах) между циклами; определяет интервалы и время жизни статуса в GitHub. Если `<= 0`, скрипт выполнится один раз.
- `debug` — глобальный флаг отладки; включает печать подробных логов для GitHub и основной логики.
- `github.max_status_length` — максимальная длина строки статуса (по умолчанию 80 символов, как на GitHub). Скрипт сначала ищет цитату, которая полностью помещается в лимит, и лишь затем прибегает к обрезанию.
- `github.dry_run` — при `true` выводит тело GraphQL‑мутации вместо реального запроса.

Статус в GitHub получает срок жизни, равный `refresh_interval_seconds`. Пока скрипт активен и `loop` включён, он будет обновлять цитату перед истечением статуса.

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