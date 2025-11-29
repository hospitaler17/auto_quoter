from unittest.mock import MagicMock, patch

import pytest

from src.github.status_client import GitHubStatusClient, GitHubStatusError, StatusResult


def _make_response(payload):
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    return response


def test_set_status_sends_mutation():
    payload = {
        "data": {
            "changeUserStatus": {
                "status": {
                    "message": '"Quote" — Source',
                    "emoji": ":speech_balloon:",
                    "expiresAt": "2025-01-01T00:00:00Z",
                }
            }
        }
    }

    with patch('requests.Session.post', return_value=_make_response(payload)) as mock_post:
        client = GitHubStatusClient("token", default_emoji=":speech_balloon:")
        result = client.set_status('"Quote" — Source', expires_in_seconds=60)

    assert result is not None
    sent_payload = mock_post.call_args.kwargs['json']
    assert sent_payload['variables']['input']['message'] == '"Quote" — Source'
    assert sent_payload['variables']['input']['emoji'] == ":speech_balloon:"
    assert 'expiresAt' in sent_payload['variables']['input']


def test_set_status_dry_run(capsys):
    client = GitHubStatusClient(token=None, dry_run=True)
    assert client.set_status('"Quote"', expires_in_seconds=None) is None
    captured = capsys.readouterr()
    assert "Would send status mutation" in captured.out


def test_set_status_graphql_error():
    payload = {"errors": [{"message": "nope"}]}

    with patch('requests.Session.post', return_value=_make_response(payload)):
        client = GitHubStatusClient("token")
        with pytest.raises(GitHubStatusError):
            client.set_status('"Quote"')


def test_set_status_empty_status_raises():
    payload = {"data": {"changeUserStatus": {"status": None}}}

    with patch('requests.Session.post', return_value=_make_response(payload)):
        client = GitHubStatusClient("token")
        with pytest.raises(GitHubStatusError):
            client.set_status('"Quote"')


def test_fetch_status_returns_value():
    payload = {
        "data": {
            "viewer": {
                "status": {
                    "message": '"Quote"',
                    "emoji": ":speech_balloon:",
                    "expiresAt": "2025-01-01T00:00:00Z",
                }
            }
        }
    }

    with patch('requests.Session.post', return_value=_make_response(payload)) as mock_post:
        client = GitHubStatusClient("token")
        status = client.fetch_status()

    assert status is not None
    assert status.message == '\"Quote\"'
    args = mock_post.call_args.kwargs
    assert 'query' in args['json']


def test_verify_status_mismatch():
    payload = {
        "data": {
            "viewer": {
                "status": {
                    "message": '"Another"',
                    "emoji": None,
                    "expiresAt": None,
                }
            }
        }
    }

    with patch('requests.Session.post', return_value=_make_response(payload)):
        client = GitHubStatusClient("token")
        ok, current = client.verify_status('"Expected"', attempts=1)

    assert ok is False
    assert current is not None
    assert current.message == '"Another"'


def test_verify_status_eventual_success():
    client = GitHubStatusClient("token")
    statuses = [
        StatusResult(message='"Old"', emoji=None, expires_at=None),
        StatusResult(message='"Wanted"', emoji=None, expires_at=None),
    ]

    fetch_mock = MagicMock(side_effect=statuses)
    client.fetch_status = fetch_mock  # type: ignore[assignment]

    with patch('time.sleep', return_value=None):
        ok, result = client.verify_status('"Wanted"', attempts=2, delay_seconds=0.1)

    assert ok is True
    assert result is not None and result.message == '"Wanted"'
    assert fetch_mock.call_count == 2
