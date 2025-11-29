from main import (
    DEFAULT_MAX_STATUS_LENGTH,
    TRUNCATION_SUFFIX,
    enforce_status_length,
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
