"""Privacy-preserving ntfy notification helper."""

from __future__ import annotations

import urllib.error
import urllib.parse
import urllib.request


class NotificationError(RuntimeError):
    """A safe-to-display ntfy failure."""


def notification_message(*, count: int = 0, test: bool = False) -> str:
    """Return a generic body that cannot contain repository metadata."""
    if test:
        return "Test de notification réussi. Aucune donnée de dépôt n’a été transmise."
    return (
        f"Le rapport hebdomadaire est prêt pour {count} dépôt(s). "
        "Quota Codex : inconnu. Ouvrir l’exécution GitHub privée."
    )


def send_notification(
    topic_url: str,
    message: str,
    *,
    click_url: str | None = None,
    token: str | None = None,
    timeout: int = 20,
    allow_http: bool = False,
) -> None:
    parsed = urllib.parse.urlparse(topic_url)
    if parsed.scheme != "https" and not (allow_http and parsed.scheme == "http"):
        raise NotificationError("The ntfy topic URL must use HTTPS")
    if not parsed.netloc or parsed.query or parsed.fragment:
        raise NotificationError("The ntfy topic URL is invalid")
    headers = {
        "Content-Type": "text/plain; charset=utf-8",
        "Title": "Maintenance hebdomadaire",
        "Priority": "default",
        "Tags": "wrench",
    }
    if click_url:
        click = urllib.parse.urlparse(click_url)
        if click.scheme != "https" or not click.netloc:
            raise NotificationError("The click URL must use HTTPS")
        headers["Click"] = click_url
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(topic_url, data=message.encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if not 200 <= response.status < 300:
                raise NotificationError(f"ntfy returned HTTP {response.status}")
    except urllib.error.HTTPError as exc:
        raise NotificationError(f"ntfy returned HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise NotificationError("ntfy is unreachable") from exc
