"""Small GitHub REST client using only Python's standard library."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


class GitHubError(RuntimeError):
    """A safe-to-display GitHub API failure."""


@dataclass
class GitHubClient:
    token: str
    api_url: str = "https://api.github.com"
    timeout: int = 30

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        query = urllib.parse.urlencode(params or {})
        url = f"{self.api_url.rstrip('/')}/{path.lstrip('/')}"
        if query:
            url = f"{url}?{query}"
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "User-Agent": "codex-weekly-maintenance/1",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            # Never include response bodies: they can contain private metadata.
            raise GitHubError(f"GitHub API returned HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise GitHubError("GitHub API is unreachable") from exc
