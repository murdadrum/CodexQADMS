from __future__ import annotations

import json
import unittest
from pathlib import Path

from apps.api.src.figma_import_endpoint import post_tokens_import_figma
from packages.contracts import CanonicalToken, CanonicalTokenModel
from packages.rules.demo_rule import evaluate_token_coverage

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "design" / "tokens" / "figma"


class FigmaImportTests(unittest.TestCase):
    def test_valid_figma_import_normalizes_successfully(self) -> None:
        payload = (FIXTURES / "sample-figma-tokens.json").read_bytes()

        status, response = post_tokens_import_figma("source-demo", payload)

        self.assertEqual(status, 200)
        self.assertTrue(response["validation"]["valid"])
        self.assertEqual(response["token_version"]["source"], "figma_export")
        self.assertEqual(response["source_id"], "source-demo")
        self.assertIn("imported_at", response)
        self.assertGreater(response["token_version"]["token_counts"]["color"], 0)

    def test_invalid_figma_import_returns_validation_errors(self) -> None:
        payload = (FIXTURES / "invalid-figma-tokens.json").read_bytes()

        status, response = post_tokens_import_figma("source-demo", payload)

        self.assertEqual(status, 422)
        self.assertFalse(response["validation"]["valid"])
        self.assertGreaterEqual(len(response["validation"]["errors"]), 1)

    def test_rules_are_source_agnostic_for_canonical_tokens(self) -> None:
        payload = json.loads((FIXTURES / "sample-figma-tokens.json").read_text())
        _, response = post_tokens_import_figma("source-demo", json.dumps(payload).encode("utf-8"))

        figma_canonical = CanonicalTokenModel(
            source=response["token_version"]["source"],
            tokens=[CanonicalToken(**token) for token in response["token_version"]["tokens"]],
        )

        manual_canonical = CanonicalTokenModel(
            source="manual_upload",
            tokens=[CanonicalToken(**token) for token in response["token_version"]["tokens"]],
        )

        figma_eval = evaluate_token_coverage(figma_canonical)
        manual_eval = evaluate_token_coverage(manual_canonical)

        self.assertEqual(figma_eval["token_counts"], manual_eval["token_counts"])
        self.assertEqual(figma_eval["total_tokens"], manual_eval["total_tokens"])

    def test_response_contains_ui_provenance_metadata(self) -> None:
        payload = (FIXTURES / "sample-figma-tokens.json").read_bytes()

        status, response = post_tokens_import_figma("source-xyz", payload)

        self.assertEqual(status, 200)
        self.assertEqual(response["source_id"], "source-xyz")
        self.assertEqual(response["token_version"]["source"], "figma_export")
        self.assertIsInstance(response["imported_at"], str)
        self.assertIsInstance(response["version_id"], str)

    def test_theme_config_format_imports_successfully(self) -> None:
        payload = (FIXTURES / "theme-config.json").read_bytes()

        status, response = post_tokens_import_figma("source-theme", payload)

        self.assertEqual(status, 200)
        self.assertTrue(response["validation"]["valid"])
        counts = response["token_version"]["token_counts"]
        self.assertGreaterEqual(counts.get("color", 0), 1)
        self.assertGreaterEqual(counts.get("radius", 0), 1)
        self.assertGreaterEqual(counts.get("typography", 0), 1)


if __name__ == "__main__":
    unittest.main()
