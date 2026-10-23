from __future__ import annotations

import unittest

from weekly_maintenance.cli import CredentialError, build_clients
from weekly_maintenance.core import RepositoryConfig


class FakeClient:
    def __init__(self, token):
        self.token = token


class CredentialTests(unittest.TestCase):
    def test_builds_only_required_distinct_clients(self):
        clients = build_clients(
            [
                RepositoryConfig("acme/one", "github_1"),
                RepositoryConfig("globex/two", "github_2"),
            ],
            {
                "MAINTENANCE_GITHUB_TOKEN_1": "token-one",
                "MAINTENANCE_GITHUB_TOKEN_2": "token-two",
            },
            client_factory=FakeClient,
        )
        self.assertEqual(clients["github_1"].token, "token-one")
        self.assertEqual(clients["github_2"].token, "token-two")

    def test_fails_closed_when_selected_secret_is_missing(self):
        with self.assertRaisesRegex(CredentialError, "TOKEN_2"):
            build_clients(
                [RepositoryConfig("globex/two", "github_2")],
                {"MAINTENANCE_GITHUB_TOKEN_1": "token-one"},
                client_factory=FakeClient,
            )

    def test_rejects_reusing_one_token_for_two_owners(self):
        with self.assertRaisesRegex(CredentialError, "must be distinct"):
            build_clients(
                [
                    RepositoryConfig("acme/one", "github_1"),
                    RepositoryConfig("globex/two", "github_2"),
                ],
                {
                    "MAINTENANCE_GITHUB_TOKEN_1": "same-token",
                    "MAINTENANCE_GITHUB_TOKEN_2": "same-token",
                },
                client_factory=FakeClient,
            )


if __name__ == "__main__":
    unittest.main()
