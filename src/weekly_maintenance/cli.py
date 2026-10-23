"""Command-line interface."""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from .core import collect_repository, load_config, seven_day_window, write_outputs
from .github import GitHubClient
from .notify import send_notification


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
        token = os.environ.get("MAINTENANCE_GITHUB_TOKEN", "")
        if not token:
            raise SystemExit("MAINTENANCE_GITHUB_TOKEN is required")
        now = datetime.fromisoformat(args.now.replace("Z", "+00:00")) if args.now else datetime.now(timezone.utc)
        since, until = seven_day_window(now)
        client = GitHubClient(token=token)
        repositories = load_config(args.config)
        activities = [collect_repository(client, repo, since, until) for repo in repositories]
        write_outputs(args.output, activities)
        print(f"Generated {len(activities)} repository report(s).")
        return 0

    topic_url = os.environ.get("NTFY_TOPIC_URL", "")
    if not topic_url:
        raise SystemExit("NTFY_TOPIC_URL is required")
    if args.test:
        message = "Test de notification réussi. Aucune donnée de dépôt n’a été transmise."
    else:
        message = (
            f"Le rapport hebdomadaire est prêt pour {args.count} dépôt(s). "
            "Quota Codex : inconnu. Ouvrir l’exécution GitHub privée."
        )
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
