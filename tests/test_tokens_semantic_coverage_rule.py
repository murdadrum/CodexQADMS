from __future__ import annotations

import unittest

from packages.contracts import CanonicalToken, CanonicalTokenModel
from packages.rules import evaluate_tokens_semantic_coverage


class TokensSemanticCoverageRuleTests(unittest.TestCase):
    def test_rule_passes_when_required_states_exist(self) -> None:
        model = CanonicalTokenModel(
            source="manual_upload",
            tokens=[
                CanonicalToken("color", "color.button.primary", "button.primary", "color", "#1f936d"),
                CanonicalToken("color", "color.button.primary.hover", "button.primary.hover", "color", "#197c5d"),
                CanonicalToken("color", "color.button.primary.focus", "button.primary.focus", "color", "#166d52"),
                CanonicalToken("color", "color.button.primary.disabled", "button.primary.disabled", "color", "#8bbcae"),
            ],
        )

        result = evaluate_tokens_semantic_coverage(model)

        self.assertEqual(result.rule_id, "TOKENS_SEMANTIC_COVERAGE")
        self.assertEqual(result.status, "pass")
        self.assertEqual(result.violation_count, 0)

    def test_rule_flags_missing_states(self) -> None:
        model = CanonicalTokenModel(
            source="manual_upload",
            tokens=[
                CanonicalToken("color", "color.button.primary", "button.primary", "color", "#1f936d"),
                CanonicalToken("color", "color.button.primary.hover", "button.primary.hover", "color", "#197c5d"),
            ],
        )

        result = evaluate_tokens_semantic_coverage(model)

        self.assertEqual(result.status, "fail")
        codes = {violation.code for violation in result.violations}
        self.assertIn("MISSING_SEMANTIC_STATES", codes)

        payload = result.to_dict()
        self.assertGreaterEqual(payload["violation_count"], 1)
        first = payload["violations"][0]
        self.assertIn("fix_hint", first)
        self.assertIn("evidence", first)

    def test_rule_flags_missing_base_token(self) -> None:
        model = CanonicalTokenModel(
            source="manual_upload",
            tokens=[
                CanonicalToken("color", "color.link.primary.hover", "link.primary.hover", "color", "#115f46"),
                CanonicalToken("color", "color.link.primary.focus", "link.primary.focus", "color", "#0f533d"),
                CanonicalToken("color", "color.link.primary.disabled", "link.primary.disabled", "color", "#73ad9b"),
            ],
        )

        result = evaluate_tokens_semantic_coverage(model)

        self.assertEqual(result.status, "fail")
        codes = {violation.code for violation in result.violations}
        self.assertIn("MISSING_BASE_STATE", codes)


if __name__ == "__main__":
    unittest.main()
