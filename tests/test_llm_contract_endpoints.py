from __future__ import annotations

import json
import unittest

from apps.api.src.llm_contract_endpoints import post_violation_explain, post_violation_fix_suggest


def _sample_payload() -> dict:
    return {
        "violation": {
            "rule_id": "TOKENS_NAMING",
            "code": "PATH_FORMAT",
            "title": "Token naming format issue",
            "description": "Token path/name should be lowercase dot-safe values.",
            "evidence": {"token_path": "color.Primary"},
            "fix_hint": {"action": "rename_token", "token_path": "color.Primary", "recommended": "color.primary"},
        }
    }


class LlmContractEndpointTests(unittest.TestCase):
    def test_violation_explain_contract_response(self) -> None:
        status, response = post_violation_explain("source-llm", json.dumps(_sample_payload()).encode("utf-8"))

        self.assertEqual(status, 200)
        self.assertEqual(response["source_id"], "source-llm")
        self.assertIn("summary", response)
        self.assertIn("evidence_citations", response)
        self.assertIn("model", response)

    def test_violation_fix_suggest_contract_response(self) -> None:
        status, response = post_violation_fix_suggest("source-llm", json.dumps(_sample_payload()).encode("utf-8"))

        self.assertEqual(status, 200)
        self.assertEqual(response["source_id"], "source-llm")
        self.assertTrue(len(response["suggested_changes"]) >= 1)
        self.assertTrue(len(response["verification_steps"]) >= 1)

    def test_llm_contract_rejects_missing_violation(self) -> None:
        status, response = post_violation_explain("source-llm", json.dumps({"foo": "bar"}).encode("utf-8"))

        self.assertEqual(status, 400)
        self.assertEqual(response["error"]["code"], "invalid_llm_payload")


if __name__ == "__main__":
    unittest.main()
