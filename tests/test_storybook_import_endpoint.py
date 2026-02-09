from __future__ import annotations

import json
import unittest

from apps.api.src.storybook_endpoint import post_storybook_source_import


class StorybookImportEndpointTests(unittest.TestCase):
    def test_storybook_import_valid_payload(self) -> None:
        payload = {
            "storybook_url": "https://storybook.example.com",
            "version_label": "2026.02.09",
            "components": [
                {
                    "component_id": "button",
                    "title": "Inputs/Button",
                    "stories": ["default", "hover", "disabled"],
                }
            ],
            "metadata": {"commit": "abc123"},
        }

        status, response = post_storybook_source_import("source-storybook", json.dumps(payload).encode("utf-8"))

        self.assertEqual(status, 200)
        self.assertEqual(response["source_id"], "source-storybook")
        self.assertEqual(response["component_count"], 1)
        self.assertEqual(response["story_count"], 3)
        self.assertEqual(response["components"][0]["component_id"], "button")
        self.assertIn("ingestion_id", response)

    def test_storybook_import_requires_valid_url(self) -> None:
        payload = {"components": []}

        status, response = post_storybook_source_import("source-storybook", json.dumps(payload).encode("utf-8"))

        self.assertEqual(status, 400)
        self.assertEqual(response["error"]["code"], "invalid_storybook_payload")

    def test_storybook_import_requires_component_story_array(self) -> None:
        payload = {
            "storybook_url": "https://storybook.example.com",
            "components": [{"component_id": "button", "stories": "default"}],
        }

        status, response = post_storybook_source_import("source-storybook", json.dumps(payload).encode("utf-8"))

        self.assertEqual(status, 400)
        self.assertEqual(response["error"]["code"], "invalid_storybook_payload")


if __name__ == "__main__":
    unittest.main()
