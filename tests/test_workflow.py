from __future__ import annotations

import re
import json
import unittest
from pathlib import Path


WORKFLOW = Path(__file__).parents[1] / ".github" / "workflows" / "weekly-maintenance.yml"
SCHEDULE = Path(__file__).parents[1] / "config" / "schedule.json"


class WorkflowSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_weekly_schedule_and_manual_execution(self):
        self.assertIn("workflow_dispatch:", self.workflow)
        self.assertIn("  schedule:\n    - cron: '17 7 * * 1'", self.workflow)
        self.assertIn("github.event_name == 'schedule'", self.workflow)
        schedule = json.loads(SCHEDULE.read_text(encoding="utf-8"))
        self.assertEqual(
            schedule,
            {"enabled": True, "cron_utc": "17 7 * * 1", "timezone": "Europe/Paris"},
        )

    def test_has_no_write_permission(self):
        self.assertRegex(self.workflow, r"permissions:\n\s+contents: read")
        self.assertNotRegex(self.workflow, r"(?m)^\s+[a-z-]+: write\s*$")

    def test_requires_private_orchestrator_before_collection(self):
        private_guard = self.workflow.index("Require a private orchestrator repository")
        collection = self.workflow.index("Collect seven days")
        self.assertLess(private_guard, collection)
        self.assertIn("github.event.repository.private", self.workflow)

    def test_uses_two_distinct_secret_slots_and_no_legacy_slot(self):
        self.assertIn("secrets.MAINTENANCE_GITHUB_TOKEN_1", self.workflow)
        self.assertIn("secrets.MAINTENANCE_GITHUB_TOKEN_2", self.workflow)
        self.assertNotIn("secrets.MAINTENANCE_GITHUB_TOKEN }}", self.workflow)

    def test_keeps_both_mobile_summary_and_zip_artifact(self):
        self.assertIn("$GITHUB_STEP_SUMMARY", self.workflow)
        self.assertIn("actions/upload-artifact@", self.workflow)
        self.assertIn("retention-days: 7", self.workflow)

    def test_report_notification_requires_at_least_one_task(self):
        self.assertIn("steps.report.outputs.count != '0'", self.workflow)
        self.assertEqual(self.workflow.count("Send generic completion push"), 1)


if __name__ == "__main__":
    unittest.main()
