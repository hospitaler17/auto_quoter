import time
from typing import Any, Dict, Optional

from src.core.builders import build_parser, build_github_client
from src.core.selection import enforce_status_length, select_quote_for_length, fetch_quote_with_retries
from src.parser.site_parser import QuoteParser
from src.github.status_client import GitHubStatusClient, GitHubStatusError


DEFAULT_MAX_STATUS_LENGTH = 80


def update_once(
    parser: QuoteParser,
    github_client: Optional[GitHubStatusClient],
    refresh_interval: int,
    max_status_length: int,
    github_enabled: bool,
    parser_max_attempts: int,
    parser_retry_interval: float,
) -> bool:
    try:
        selected_entry, status_message, attempts, within_limit = fetch_quote_with_retries(
            parser,
            max_status_length,
            parser_max_attempts,
            parser_retry_interval,
        )
    except Exception as exc:  # pragma: no cover - network errors
        print(f"Ошибка при получении страницы: {exc}")
        return False

    if not status_message:
        print("Нет строки для обновления статуса GitHub.")
        return True

    quote = selected_entry.get('quote') if selected_entry else None
    source = selected_entry.get('source') if selected_entry else None

    if attempts > 1 and within_limit:
        print(f"Цитата найдена за {attempts} попыток.")
    elif not within_limit:
        print(
            "Подходящую по длине цитату найти не удалось. Используем первый результат"
            " и при необходимости обрежем."
        )

    if quote:
        print(f"QUOTE: {quote}")
    else:
        print("QUOTE: не найдено")

    if source:
        print(f"SOURCE: {source}")
    else:
        print("SOURCE: не найдено")

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
    from src.core.config import load_config

    config = load_config()
    parser_cfg = config.get('parser') or {}
    parser = build_parser(config)
    github_config = config.get('github') or {}
    # top-level loop and interval
    loop_enabled = bool(config.get('loop', True))
    refresh_interval = int(config.get('refresh_interval_seconds') or 0)
    global_debug = bool(config.get('debug', False))

    parser_max_attempts = int(
        parser_cfg.get('max_attempts', 0) or 0
    )
    if parser_max_attempts < 0:
        parser_max_attempts = 0

    parser_retry_interval = float(
        parser_cfg.get('retry_interval_seconds', 1.0)
    )
    if parser_retry_interval < 0:
        parser_retry_interval = 0.0

    github_client, github_enabled = build_github_client(github_config, debug=global_debug)
    max_status_length = int(
        github_config.get('max_status_length') or DEFAULT_MAX_STATUS_LENGTH
    )

    # if loop globally disabled, force single-run
    if not loop_enabled:
        refresh_interval = 0

    # if github is enabled but we couldn't construct a client (e.g. missing token),
    # fall back to single-run to avoid repeated failing attempts
    if github_enabled and not github_client:
        refresh_interval = 0

    try:
        while True:
            success = update_once(
                parser,
                github_client,
                refresh_interval,
                max_status_length,
                github_enabled,
                parser_max_attempts,
                parser_retry_interval,
            )
            if not success:
                break

            if not refresh_interval or refresh_interval <= 0:
                break

            print(f"Повторное обновление статуса через {refresh_interval} секунд...")
            time.sleep(refresh_interval)
    except KeyboardInterrupt:
        print("Остановка по Ctrl+C.")
