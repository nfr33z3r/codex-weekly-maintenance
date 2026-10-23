"""Command-line interface."""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping

from .core import RepositoryConfig, collect_repositories, load_config, seven_day_window, write_outputs
from .github import GitHubClient
from .notify import notification_message, send_notification

CREDENTIAL_ENV = {
    "github_1": "MAINTENANCE_GITHUB_TOKEN_1",
    "github_2": "MAINTENANCE_GITHUB_TOKEN_2",
}


class CredentialError(RuntimeError):
    """Missing, unknown or reused GitHub read-only credential."""


def build_clients(
    repositories: list[RepositoryConfig],
    environ: Mapping[str, str],
    client_factory: Callable[..., GitHubClient] = GitHubClient,
) -> dict[str, GitHubClient]:
    """Resolve only explicitly required credential aliases, without fallback."""
    required = sorted({repository.credential_id for repository in repositories})
    clients: dict[str, GitHubClient] = {}
    tokens: list[str] = []
    for credential_id in required:
        env_name = CREDENTIAL_ENV.get(credential_id)
        if env_name is None:
            raise CredentialError(f"Unknown GitHub credential alias: {credential_id}")
        token = environ.get(env_name, "")
        if not token:
            raise CredentialError(f"{env_name} is required by the owner allow-list")
        tokens.append(token)
        clients[credential_id] = client_factory(token=token)
    if len(tokens) != len(set(tokens)):
        raise CredentialError("Configured GitHub credentials must be distinct")
    return clients


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="weekly-maintenance")
    commands = root.add_subparsers(dest="command", required=True)
    collect = commands.add_parser("collect", help="Collect GitHub activity and generate reports")
    collect.add_argument("--config", type=Path, required=True)
    collect.add_argument("--output", type=Path, required=True)
    collect.add_argument("--now", help="Fixed ISO-8601 time for reproducible runs")

    notify = commands.add_parser("notify", help="Send a generic ntfy message")
    notify.add_argument("--count", type=int, default=0)
    notify.add_argument("--test", action="store_true")
    notify.add_argument("--click-url")
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "collect":
        now = (
            datetime.fromisoformat(args.now.replace("Z", "+00:00"))
            if args.now
            else datetime.now(timezone.utc)
        )
        since, until = seven_day_window(now)
        repositories = load_config(args.config)
        try:
            clients = build_clients(repositories, os.environ)
        except CredentialError as exc:
            raise SystemExit(str(exc)) from exc
        activities = collect_repositories(clients, repositories, since, until)
        manifest = write_outputs(args.output, activities)
        print(f"Generated {len(manifest['repositories'])} active repository report(s).")
        return 0

    topic_url = os.environ.get("NTFY_TOPIC_URL", "")
    if not topic_url:
        raise SystemExit("NTFY_TOPIC_URL is required")
    message = notification_message(count=args.count, test=args.test)
    send_notification(
        topic_url,
        message,
        click_url=args.click_url,
        token=os.environ.get("NTFY_TOKEN") or None,
    )
    print("Notification sent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
