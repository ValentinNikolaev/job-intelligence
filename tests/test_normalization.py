import unittest

from jobintel.html_to_markdown import html_to_markdown
from jobintel.normalization import normalize_company, normalize_location, record_directory_name, vacancy_fingerprint


class NormalizationTests(unittest.TestCase):
    def test_record_directory_bounds_long_company_and_preserves_full_uuid(self) -> None:
        name = record_directory_name(
            "2026-10-05T12:14:47Z", "Wooden Sword Games " * 20,
            "cb978155-40d1-43dd-b93e-d8f5c42cbd1d",
        )
        self.assertLessEqual(len(name), 56)
        self.assertTrue(name.startswith("20261005_wooden-sword-g_"))
        self.assertTrue(name.endswith("cb97815540d143ddb93ed8f5c42cbd1d"))

    def test_record_directory_does_not_collide_on_shared_uuid_prefix(self) -> None:
        names = {record_directory_name("2026-10-05T12:00:00Z", "Acme", identity)
                 for identity in ("cb978155-40d1-43dd-b93e-d8f5c42cbd1d",
                                  "cb978155-40d1-43dd-b93e-d8f5c42cbd1e")}
        self.assertEqual(2, len(names))

    def test_record_directory_handles_unicode_empty_and_non_uuid_ids(self) -> None:
        for company in ("Компания / с очень длинным названием " * 20, "<> : / ?", ""):
            with self.subTest(company=company[:20]):
                name = record_directory_name("2026-10-05T12:00:00Z", company, "id/with:unsafe?chars" * 10)
                self.assertLessEqual(len(name), 56)
                self.assertNotRegex(name, r'[<>:"/\\|?*]')
                self.assertEqual(name, record_directory_name("2026-10-05T12:00:00Z", company, "id/with:unsafe?chars" * 10))

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

