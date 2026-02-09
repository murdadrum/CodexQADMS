from __future__ import annotations

import json
import unittest
from pathlib import Path

from apps.api.src.rule_audit_endpoint import post_rule_audit
from apps.api.src.rule_audit_endpoint import post_rule_report

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "design" / "tokens" / "figma"


class RuleReportEndpointTests(unittest.TestCase):
    def test_report_contains_summary_and_violations(self) -> None:
        payload = (FIXTURES / "sample-figma-tokens.json").read_bytes()

        status, response = post_rule_report("source-report", payload)

        self.assertEqual(status, 200)
        self.assertEqual(response["source_id"], "source-report")
        self.assertIn("summary", response)
        self.assertIn("violations", response)
        self.assertIn("generated_at", response)

    def test_report_invalid_json(self) -> None:
        status, response = post_rule_report("source-report", b"{invalid")

        self.assertEqual(status, 400)
        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], "invalid_json")

    def test_report_invalid_source_id(self) -> None:
        payload = (FIXTURES / "sample-figma-tokens.json").read_bytes()
        status, response = post_rule_report("  ", payload)

        self.assertEqual(status, 400)
        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], "invalid_source_id")

    def test_report_matches_audit_summary_and_violations(self) -> None:
        payload = (FIXTURES / "sample-figma-tokens.json").read_bytes()

        audit_status, audit_response = post_rule_audit("source-report", payload)
        report_status, report_response = post_rule_report("source-report", payload)

        self.assertEqual(audit_status, 200)
        self.assertEqual(report_status, 200)
        self.assertEqual(report_response["source_id"], audit_response["source_id"])
        self.assertEqual(report_response["summary"], audit_response["summary"])
        self.assertEqual(report_response["violations"], audit_response["violations"])
        self.assertIn("generated_at", report_response)


if __name__ == "__main__":
    unittest.main()
