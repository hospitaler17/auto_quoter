"""GitHub GraphQL client for updating user status."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import requests

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

STATUS_MUTATION = """
mutation($input: ChangeUserStatusInput!) {
  changeUserStatus(input: $input) {
    status {
      message
      emoji
      expiresAt
    }
  }
}
"""

VIEWER_STATUS_QUERY = """
query {
    viewer {
        status {
            message
            emoji
            expiresAt
        }
    }
}
"""


class GitHubStatusError(RuntimeError):
    """Raised when GitHub status update fails."""


@dataclass
class StatusResult:
    message: str
    emoji: Optional[str]
    expires_at: Optional[str]


class GitHubStatusClient:
    """Small helper around GitHub's GraphQL API to change user status."""

    def __init__(
        self,
        token: Optional[str],
        api_url: str = GITHUB_GRAPHQL_URL,
        default_emoji: Optional[str] = None,
        timeout: int = 10,
        dry_run: bool = False,
        debug: bool = False,
    ) -> None:
        if not token and not dry_run:
            raise ValueError("GitHub token is required unless dry_run is True")

        self.api_url = api_url
        self.default_emoji = default_emoji
        self.timeout = timeout
        self.dry_run = dry_run or not token
        self.debug = debug
        self._session = requests.Session()
        if token:
            self._session.headers.update(
                {
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                    "Content-Type": "application/json",
                }
            )

    def set_status(
        self,
        message: str,
        *,
        emoji: Optional[str] = None,
        expires_in_seconds: Optional[int] = None,
    ) -> Optional[StatusResult]:
        """Sends a `changeUserStatus` mutation to GitHub.

        Args:
            message: Text that will appear in the status.
            emoji: Optional emoji code (":octocat:" etc.). Falls back to `default_emoji`.
            expires_in_seconds: Optional number of seconds after which the status should expire.
                When omitted or <= 0, the status stays until overwritten manually.
        Returns:
            StatusResult if the call succeeds and real request executed.
            Returns None when running in dry-run mode.
        Raises:
            GitHubStatusError: when the API rejects the request or returns GraphQL errors.
        """

        if not message:
            raise ValueError("Status message is required")

        payload = self._build_payload(message, emoji, expires_in_seconds)

        if self.debug:
            print("[debug] prepared status payload:", json.dumps(payload, ensure_ascii=False))

        if self.dry_run:
            # Helpful for local testing without a token
            print("[dry-run] Would send status mutation:")
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return None

        response = self._session.post(self.api_url, json=payload, timeout=self.timeout)
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:  # pragma: no cover - exercised via tests
            raise GitHubStatusError(f"GitHub API request failed: {exc}") from exc

        data = response.json()
        if self.debug:
            print("[debug] changeUserStatus response:", json.dumps(data, ensure_ascii=False))
        if data.get("errors"):
            raise GitHubStatusError(f"GitHub API errors: {data['errors']}")

        status_data = (data.get("data") or {}).get("changeUserStatus") or {}
        status = status_data.get("status")
        if not status:
            raise GitHubStatusError(
                "GitHub API returned empty status",
            )

        return StatusResult(
            message=status.get("message"),
            emoji=status.get("emoji"),
            expires_at=status.get("expiresAt"),
        )

    def fetch_status(self) -> Optional[StatusResult]:
        """Returns the current user status via GraphQL viewer query."""

        if self.dry_run:
            print("[dry-run] Would request current status")
            return None

        response = self._session.post(
            self.api_url,
            json={"query": VIEWER_STATUS_QUERY},
            timeout=self.timeout,
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:  # pragma: no cover - network errors
            raise GitHubStatusError(f"GitHub API request failed: {exc}") from exc

        data = response.json()
        if self.debug:
            print("[debug] viewer status response:", json.dumps(data, ensure_ascii=False))
        if data.get("errors"):
            raise GitHubStatusError(f"GitHub API errors: {data['errors']}")

        status = ((data.get("data") or {}).get("viewer") or {}).get("status")
        if not status:
            return None

        return StatusResult(
            message=status.get("message"),
            emoji=status.get("emoji"),
            expires_at=status.get("expiresAt"),
        )

    def verify_status(
        self,
        expected_message: str,
        *,
        attempts: int = 3,
        delay_seconds: float = 2.0,
    ) -> tuple[bool, Optional[StatusResult]]:
        """Checks if GitHub status matches expected text.

        Returns tuple (matched, last_status). When `dry_run` is True the method returns (True, None).
        """

        if self.dry_run:
            return True, None

        last_status: Optional[StatusResult] = None
        for attempt in range(max(1, attempts)):
            status = self.fetch_status()
            last_status = status
            if status and status.message == expected_message:
                return True, status

            if attempt < attempts - 1:
                time.sleep(max(0.0, delay_seconds))

        return False, last_status

    def _build_payload(
        self,
        message: str,
        emoji: Optional[str],
        expires_in_seconds: Optional[int],
    ) -> Dict[str, Any]:
        input_payload: Dict[str, Any] = {"message": message}

        emoji_to_use = emoji or self.default_emoji
        if emoji_to_use:
            input_payload["emoji"] = emoji_to_use

        if expires_in_seconds and expires_in_seconds > 0:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)
            iso_value = expires_at.isoformat().replace("+00:00", "Z")
            input_payload["expiresAt"] = iso_value

        return {"query": STATUS_MUTATION, "variables": {"input": input_payload}}