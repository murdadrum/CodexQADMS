from __future__ import annotations

import json
import unittest

from apps.api.src.visual_diff_endpoint import post_visual_diff_audit


class VisualDiffEndpointTests(unittest.TestCase):
    def test_visual_diff_pass_for_identical_snapshots(self) -> None:
        payload = {
            "baseline_snapshot": "component:button:default",
            "current_snapshot": "component:button:default",
            "threshold": 0.0,
        }

        status, response = post_visual_diff_audit("source-visual", json.dumps(payload).encode("utf-8"))

        self.assertEqual(status, 200)
        self.assertEqual(response["status"], "pass")
        self.assertEqual(response["summary"]["changed_bytes"], 0)

    def test_visual_diff_fail_for_different_snapshots(self) -> None:
        payload = {
            "baseline_snapshot": "component:button:default",
            "current_snapshot": "component:button:danger",
            "threshold": 0.0,
        }

        status, response = post_visual_diff_audit("source-visual", json.dumps(payload).encode("utf-8"))

        self.assertEqual(status, 200)
        self.assertEqual(response["status"], "fail")
        self.assertGreater(response["summary"]["changed_bytes"], 0)
        self.assertIn("diff_ref", response["artifacts"])

    def test_visual_diff_rejects_invalid_threshold(self) -> None:
        payload = {
            "baseline_snapshot": "a",
            "current_snapshot": "b",
            "threshold": 2.0,
        }

        status, response = post_visual_diff_audit("source-visual", json.dumps(payload).encode("utf-8"))

        self.assertEqual(status, 400)
        self.assertEqual(response["error"]["code"], "invalid_visual_diff_payload")


if __name__ == "__main__":
    unittest.main()
