from main import (
    DEFAULT_MAX_STATUS_LENGTH,
    TRUNCATION_SUFFIX,
    enforce_status_length,
    select_quote_for_length,
)


def test_enforce_status_length_no_truncation():
    message = "short status"
    result, truncated = enforce_status_length(message, DEFAULT_MAX_STATUS_LENGTH)
    assert result == message
    assert truncated is False


def test_enforce_status_length_truncates():
    message = "A" * (DEFAULT_MAX_STATUS_LENGTH + 10)
    result, truncated = enforce_status_length(message, DEFAULT_MAX_STATUS_LENGTH)
    assert truncated is True
    assert len(result) == DEFAULT_MAX_STATUS_LENGTH
    assert result.endswith(TRUNCATION_SUFFIX)


def test_enforce_status_length_respects_custom_limit():
    limit = 50
    message = "B" * 60
    result, truncated = enforce_status_length(message, limit)
    assert truncated is True
    assert len(result) == limit


def test_select_quote_for_length_prefers_entry_within_limit():
    quotes = [
        {"quote": "A" * 90, "source": "Long"},
        {"quote": "короткая", "source": "Автор"},
    ]

    entry, message = select_quote_for_length(quotes, 80)

    assert entry is quotes[1]
    assert len(message) <= 80


def test_select_quote_for_length_falls_back_to_first():
    quotes = [
        {"quote": "A" * 120, "source": "Long"},
        {"quote": "B" * 110, "source": "Also long"},
    ]

    entry, message = select_quote_for_length(quotes, 20)

    assert entry is quotes[0]
    assert message.startswith('"')
