import json
import sys
import time
from typing import Any, Dict, Optional, Tuple

from src.github.status_client import GitHubStatusClient, GitHubStatusError
from src.parser.site_parser import QuoteParser

DEFAULT_MAX_STATUS_LENGTH = 80
TRUNCATION_SUFFIX = "..."


def load_config(config_path: str = 'config.json') -> Dict[str, Any]:
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Ошибка: Файл конфигурации '{config_path}' не найден.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Ошибка: Неверный формат JSON в '{config_path}'.")
        sys.exit(1)


def build_parser(config: Dict[str, Any]) -> QuoteParser:
    return QuoteParser(
        config.get('url'),
        config.get('quote_selector'),
        config.get('source_selector'),
        config.get('source_attr', 'data-source'),
        timeout=config.get('timeout', 10),
    )


def build_github_client(
    config: Optional[Dict[str, Any]]
) -> Tuple[Optional[GitHubStatusClient], int, bool]:
    if not config:
        return None, 0, False

    enabled = config.get('enabled', True)
    refresh_interval = int(config.get('refresh_interval_seconds') or 0)

    if not enabled:
        return None, refresh_interval, False

    token = config.get('token')
    dry_run = config.get('dry_run', False)
    if not token and not dry_run:
        print("GitHub token не указан, статус обновляться не будет.")
        return None, refresh_interval, True

    client_kwargs = {
        'token': token,
        'default_emoji': config.get('emoji'),
        'timeout': config.get('timeout', 10),
        'dry_run': dry_run,
        'debug': config.get('debug', False),
    }
    if config.get('graphql_url'):
        client_kwargs['api_url'] = config['graphql_url']

    client = GitHubStatusClient(**client_kwargs)
    return client, refresh_interval, True


def format_status_message(quote: Optional[str], source: Optional[str]) -> Optional[str]:
    if not quote:
        return None
    if source:
        return f'"{quote}" — {source}'
    return f'"{quote}"'


def enforce_status_length(message: str, limit: int) -> Tuple[str, bool]:
    """Ensures the status fits GitHub's length limit (default 80 chars)."""

    limit = max(1, limit or DEFAULT_MAX_STATUS_LENGTH)

    if len(message) <= limit:
        return message, False

    if limit <= len(TRUNCATION_SUFFIX):
        return message[:limit], True

    clipped = message[: limit - len(TRUNCATION_SUFFIX)].rstrip()
    return f"{clipped}{TRUNCATION_SUFFIX}", True


def update_once(
    parser: QuoteParser,
    github_client: Optional[GitHubStatusClient],
    refresh_interval: int,
    max_status_length: int,
    github_enabled: bool,
) -> bool:
    try:
        result = parser.fetch()
    except Exception as exc:  # pragma: no cover - network errors
        print(f"Ошибка при получении страницы: {exc}")
        return False

    quote = result.get('quote')
    source = result.get('source')

    if quote:
        print(f"QUOTE: {quote}")
    else:
        print("QUOTE: не найдено")

    if source:
        print(f"SOURCE: {source}")
    else:
        print("SOURCE: не найдено")

    status_message = format_status_message(quote, source)
    if not status_message:
        print("Нет строки для обновления статуса GitHub.")
        return True

    if not github_enabled:
        return True

    if not github_client:
        return True

    status_message, truncated = enforce_status_length(status_message, max_status_length)
    if truncated:
        print(
            f"Предупреждение: статус длиннее {max_status_length} символов и был обрезан: "
            f"{status_message}"
        )

    if github_client.debug:
        print(f"[debug] formatted status message: {status_message}")

    try:
        github_client.set_status(status_message, expires_in_seconds=refresh_interval)
        matched, current_status = github_client.verify_status(
            status_message,
            attempts=3,
            delay_seconds=2.0,
        )
        if matched:
            print("Статус GitHub обновлён и подтверждён.")
        else:
            actual_text = current_status.message if current_status else "<пусто>"
            print(
                "Предупреждение: GitHub статус не совпадает с ожидаемым. "
                f"Текущее значение: {actual_text}"
            )
    except GitHubStatusError as err:
        print(f"Не удалось обновить статус GitHub: {err}")
        return False

    return True


def main() -> None:
    config = load_config()
    parser = build_parser(config)
    github_config = config.get('github') or {}
    github_client, refresh_interval, github_enabled = build_github_client(github_config)
    max_status_length = int(
        github_config.get('max_status_length') or DEFAULT_MAX_STATUS_LENGTH
    )

    if not github_client and github_enabled:
        refresh_interval = 0

    try:
        while True:
            success = update_once(
                parser,
                github_client,
                refresh_interval,
                max_status_length,
                github_enabled,
            )
            if not success:
                break

            if not refresh_interval or refresh_interval <= 0:
                break

            print(f"Повторное обновление статуса через {refresh_interval} секунд...")
            time.sleep(refresh_interval)
    except KeyboardInterrupt:
        print("Остановка по Ctrl+C.")


if __name__ == "__main__":
    main()
