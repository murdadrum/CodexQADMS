from __future__ import annotations

import json
import unittest
from pathlib import Path

from apps.api.src.rule_audit_endpoint import post_rule_audit

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "design" / "tokens" / "figma"


class RuleAuditEndpointTests(unittest.TestCase):
    def test_rule_audit_returns_summary_and_violations(self) -> None:
        payload = {
            "color": {
                "Text": {"Primary": {"$value": "#9ca3af", "$type": "color"}},
                "bg": {"canvas": {"$value": "#ffffff", "$type": "color"}},
                "button": {
                    "primary": {"$value": "#1f936d", "$type": "color"},
                    "primary": {"hover": {"$value": "#1a7f5f", "$type": "color"}},
                },
            },
            "spacing": {
                "100": {"$value": "4", "$type": "dimension"},
                "500": {"$value": "24", "$type": "dimension"},
            },
            "typography": {
                "body": {
                    "sm": {"$value": "12", "$type": "dimension"},
                    "lg": {"$value": "18", "$type": "dimension"},
                }
            },
        }

        status, response = post_rule_audit("source-audit", json.dumps(payload).encode("utf-8"))

        self.assertEqual(status, 200)
        self.assertEqual(response["source_id"], "source-audit")
        self.assertIn("summary", response)
        self.assertIn("violations", response)
        self.assertIn("by_severity", response["summary"])
        self.assertIsInstance(response["summary"]["total_violations"], int)

        if response["violations"]:
            first = response["violations"][0]
            self.assertIn("category", first)
            self.assertIn("severity", first)
            self.assertIn("rule_id", first)
            self.assertIn("fix_hint", first)

    def test_rule_audit_invalid_json_uses_error_envelope(self) -> None:
        status, response = post_rule_audit("source-audit", b"{invalid")

        self.assertEqual(status, 400)
        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], "invalid_json")

    def test_rule_audit_invalid_source_id_uses_error_envelope(self) -> None:
        payload = (FIXTURES / "sample-figma-tokens.json").read_bytes()
        status, response = post_rule_audit("  ", payload)

        self.assertEqual(status, 400)
        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], "invalid_source_id")


if __name__ == "__main__":
    unittest.main()
