from __future__ import annotations

import unittest

from packages.contracts import CanonicalToken, CanonicalTokenModel
from packages.rules import evaluate_tokens_scale


class TokensScaleRuleTests(unittest.TestCase):
    def test_rule_passes_for_consistent_scales(self) -> None:
        model = CanonicalTokenModel(
            source="manual_upload",
            tokens=[
                CanonicalToken("spacing", "spacing.scale.100", "scale.100", "dimension", "4"),
                CanonicalToken("spacing", "spacing.scale.200", "scale.200", "dimension", "8"),
                CanonicalToken("spacing", "spacing.scale.300", "scale.300", "dimension", "12"),
                CanonicalToken("typography", "typography.body.sm", "body.sm", "dimension", "12"),
                CanonicalToken("typography", "typography.body.md", "body.md", "dimension", "14"),
                CanonicalToken("typography", "typography.body.lg", "body.lg", "dimension", "16"),
            ],
        )

        result = evaluate_tokens_scale(model)

        self.assertEqual(result.rule_id, "TOKENS_SCALE")
        self.assertEqual(result.status, "pass")
        self.assertEqual(result.violation_count, 0)

    def test_rule_detects_large_gap(self) -> None:
        model = CanonicalTokenModel(
            source="manual_upload",
            tokens=[
                CanonicalToken("spacing", "spacing.scale.100", "scale.100", "dimension", "4"),
                CanonicalToken("spacing", "spacing.scale.200", "scale.200", "dimension", "8"),
                CanonicalToken("spacing", "spacing.scale.500", "scale.500", "dimension", "24"),
            ],
        )

        result = evaluate_tokens_scale(model)

        self.assertEqual(result.status, "fail")
        codes = {violation.code for violation in result.violations}
        self.assertIn("SCALE_GAP", codes)

    def test_rule_detects_invalid_numeric_and_non_positive_values(self) -> None:
        model = CanonicalTokenModel(
            source="manual_upload",
            tokens=[
                CanonicalToken("spacing", "spacing.scale.bad", "scale.bad", "dimension", "abc"),
                CanonicalToken("spacing", "spacing.scale.zero", "scale.zero", "dimension", "0"),
                CanonicalToken("typography", "typography.body.neg", "body.neg", "dimension", -2),
            ],
        )

        result = evaluate_tokens_scale(model)

        self.assertEqual(result.status, "fail")
        codes = {violation.code for violation in result.violations}
        self.assertIn("INVALID_NUMERIC_VALUE", codes)
        self.assertIn("NON_POSITIVE_VALUE", codes)


if __name__ == "__main__":
    unittest.main()
