import unittest

from jobintel.html_to_markdown import html_to_markdown
from jobintel.normalization import normalize_company, normalize_location, vacancy_fingerprint


class NormalizationTests(unittest.TestCase):
    def test_fingerprint_normalizes_safe_variants(self) -> None:
        first = vacancy_fingerprint("Acme Ltd.", "Senior Backend Engineer", "Work from home - Europe")
        second = vacancy_fingerprint("  ACME  ", "Senior—Backend Engineer", "Remote, Europe")
        self.assertEqual(first, second)

    def test_company_suffix_only_removed_at_end(self) -> None:
        self.assertEqual(normalize_company("Acme Incorporated"), "acme")
        self.assertEqual(normalize_company("Inc Research Labs"), "inc research labs")

    def test_remote_normalization_preserves_geography(self) -> None:
        self.assertEqual(normalize_location("Fully Remote — EU"), "remote eu")
        self.assertNotEqual(normalize_location("Remote EU"), normalize_location("Remote US"))

    def test_html_conversion_removes_script_and_preserves_structure(self) -> None:
        markdown = html_to_markdown(
            "&lt;h2&gt;Requirements&lt;/h2&gt;&lt;ul&gt;&lt;li&gt;Python&lt;/li&gt;&lt;/ul&gt;"
            "<script>tracking()</script><p><a href='https://example.test'>Apply</a></p>"
        )
        self.assertIn("## Requirements", markdown)
        self.assertIn("- Python", markdown)
        self.assertIn("[Apply](https://example.test)", markdown)
        self.assertNotIn("tracking", markdown)


if __name__ == "__main__":
    unittest.main()

