from __future__ import annotations

import unittest

from packages.contracts import CanonicalToken, CanonicalTokenModel
from packages.rules import evaluate_tokens_naming


class TokensNamingRuleTests(unittest.TestCase):
    def test_rule_passes_for_dot_safe_lowercase_tokens(self) -> None:
        model = CanonicalTokenModel(
            source="manual_upload",
            tokens=[
                CanonicalToken(
                    group="color",
                    path="color.text.primary",
                    name="text.primary",
                    token_type="color",
                    value="#111827",
                ),
                CanonicalToken(
                    group="spacing",
                    path="spacing.scale.100",
                    name="scale.100",
                    token_type="dimension",
                    value="4",
                ),
            ],
        )

        result = evaluate_tokens_naming(model)

        self.assertEqual(result.rule_id, "TOKENS_NAMING")
        self.assertEqual(result.status, "pass")
        self.assertEqual(result.violation_count, 0)
        self.assertEqual(result.to_dict()["violation_count"], 0)

    def test_rule_emits_violations_with_evidence_and_fix_hint(self) -> None:
        model = CanonicalTokenModel(
            source="manual_upload",
            tokens=[
                CanonicalToken(
                    group="color",
                    path="Color.Text Primary",
                    name="Text Primary",
                    token_type="color",
                    value="#ffffff",
                )
            ],
        )

        result = evaluate_tokens_naming(model)

        self.assertEqual(result.status, "fail")
        self.assertGreaterEqual(result.violation_count, 2)

        payload = result.to_dict()
        first = payload["violations"][0]
        self.assertIn("evidence", first)
        self.assertIn("fix_hint", first)
        self.assertEqual(first["rule_id"], "TOKENS_NAMING")
        self.assertIn(first["fix_hint"]["action"], {"rename_token"})

    def test_rule_flags_missing_group_prefix(self) -> None:
        model = CanonicalTokenModel(
            source="manual_upload",
            tokens=[
                CanonicalToken(
                    group="color",
                    path="semantic.text.primary",
                    name="semantic.text.primary",
                    token_type="color",
                    value="#111827",
                )
            ],
        )

        result = evaluate_tokens_naming(model)

        self.assertEqual(result.status, "fail")
        codes = {violation.code for violation in result.violations}
        self.assertIn("GROUP_PREFIX", codes)


if __name__ == "__main__":
    unittest.main()
