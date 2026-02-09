from __future__ import annotations

import unittest

from packages.contracts import CanonicalToken, CanonicalTokenModel
from packages.rules import evaluate_a11y_contrast


class A11yContrastRuleTests(unittest.TestCase):
    def test_rule_passes_for_high_contrast_pairs(self) -> None:
        model = CanonicalTokenModel(
            source="manual_upload",
            tokens=[
                CanonicalToken("color", "color.text.primary", "text.primary", "color", "#111827"),
                CanonicalToken("color", "color.bg.canvas", "bg.canvas", "color", "#ffffff"),
            ],
        )

        result = evaluate_a11y_contrast(model)

        self.assertEqual(result.rule_id, "A11Y_CONTRAST")
        self.assertEqual(result.status, "pass")
        self.assertEqual(result.violation_count, 0)

    def test_rule_flags_low_contrast_pair(self) -> None:
        model = CanonicalTokenModel(
            source="manual_upload",
            tokens=[
                CanonicalToken("color", "color.text.subtle", "text.subtle", "color", "#9ca3af"),
                CanonicalToken("color", "color.bg.canvas", "bg.canvas", "color", "#ffffff"),
            ],
        )

        result = evaluate_a11y_contrast(model)

        self.assertEqual(result.status, "fail")
        self.assertGreaterEqual(result.violation_count, 1)
        violation = result.violations[0]
        self.assertEqual(violation.code, "LOW_CONTRAST")
        self.assertIn("contrast_ratio", violation.evidence)
        self.assertIn("required_ratio", violation.fix_hint)

    def test_rule_flags_invalid_color_values(self) -> None:
        model = CanonicalTokenModel(
            source="manual_upload",
            tokens=[
                CanonicalToken("color", "color.text.primary", "text.primary", "color", "not-a-color"),
                CanonicalToken("color", "color.bg.canvas", "bg.canvas", "color", "#ffffff"),
            ],
        )

        result = evaluate_a11y_contrast(model)

        self.assertEqual(result.status, "fail")
        codes = {violation.code for violation in result.violations}
        self.assertIn("INVALID_TEXT_COLOR", codes)

    def test_rule_supports_hsl_and_rgb_formats(self) -> None:
        model = CanonicalTokenModel(
            source="manual_upload",
            tokens=[
                CanonicalToken("color", "color.text.primary", "text.primary", "color", "hsl(0, 0%, 0%)"),
                CanonicalToken("color", "color.bg.canvas", "bg.canvas", "color", "rgb(255, 255, 255)"),
            ],
        )

        result = evaluate_a11y_contrast(model)

        self.assertEqual(result.status, "pass")
        self.assertEqual(result.violation_count, 0)


if __name__ == "__main__":
    unittest.main()
