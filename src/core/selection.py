import time
from typing import Any, Dict, List, Optional, Tuple


DEFAULT_MAX_STATUS_LENGTH = 80
TRUNCATION_SUFFIX = "..."


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


def select_quote_for_length(
    candidates: List[Dict[str, Optional[str]]],
    max_status_length: int,
) -> Tuple[Optional[Dict[str, Optional[str]]], Optional[str]]:
    """Возвращает первую цитату, которая помещается в лимит, либо первую доступную."""

    fallback_entry: Optional[Dict[str, Optional[str]]] = None
    fallback_message: Optional[str] = None

    for entry in candidates:
        message = format_status_message(entry.get('quote'), entry.get('source'))
        if not message:
            continue

        if fallback_entry is None:
            fallback_entry = entry
            fallback_message = message

        if len(message) <= max_status_length:
            return entry, message

    return fallback_entry, fallback_message


def fetch_quote_with_retries(
    parser: Any,
    max_status_length: int,
    max_attempts: int,
    retry_interval: float,
) -> Tuple[Optional[Dict[str, Optional[str]]], Optional[str], int, bool]:
    """Повторяет запрос страницы, пока не найдёт цитату в пределах лимита."""

    attempts = 0
    fallback_entry: Optional[Dict[str, Optional[str]]] = None
    fallback_message: Optional[str] = None
    unlimited = max_attempts <= 0

    while True:
        attempts += 1
        results = parser.fetch_all()
        if results:
            entry, message = select_quote_for_length(results, max_status_length)
            if message:
                if fallback_entry is None:
                    fallback_entry = entry
                    fallback_message = message
                if len(message) <= max_status_length:
                    return entry, message, attempts, True

        if not unlimited and attempts >= max_attempts:
            break

        if retry_interval > 0:
            time.sleep(retry_interval)

    return fallback_entry, fallback_message, attempts, False
