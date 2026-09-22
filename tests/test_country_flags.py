from __future__ import annotations

import unittest

from jobintel.country_flags import country_codes_for_location, render_country_flags


class CountryFlagTests(unittest.TestCase):
    def test_explicit_countries_and_translated_names(self) -> None:
        cases = {
            "Remote Italy / Hybrid Bologna": ["IT"],
            "Hamburg, Deutschland": ["DE"],
            "Италия, Німеччина, Polska, España, France": ["IT", "DE", "PL", "ES", "FR"],
            "London, UK; Ireland; USA; UAE": ["GB", "IE", "US", "AE"],
            "Northern Ireland / Guinea-Bissau": ["GB", "GW"],
            "Remote, United Kingdom of Great Britain and Northern Ireland": ["GB"],
            "IT / DE; FR, GB": ["IT", "DE", "FR", "GB"],
            "Kosovo": ["XK"],
        }
        for location, expected in cases.items():
            with self.subTest(location=location):
                self.assertEqual(expected, country_codes_for_location(location))

    def test_regions_unknown_cities_and_ordinary_words_have_no_flags(self) -> None:
        for location in (None, "", [], "Worldwide", "Remote in Europe", "EMEA", "Remote",
                         "Anywhere", "Unknown", "Leipzig", "San Francisco, CA", "Remote IT role"):
            with self.subTest(location=location):
                self.assertEqual([], country_codes_for_location(location))

    def test_deduplicates_aliases_in_location_order(self) -> None:
        self.assertEqual(
            ["DE", "IT", "GB", "US"],
            country_codes_for_location("Germany, Italy, Deutschland, UK, United Kingdom, USA, US"),
        )

    def test_caps_rendering_at_five_unique_flags(self) -> None:
        codes = country_codes_for_location("Italy, Germany, France, Spain, Poland, Portugal, Ireland")
        self.assertEqual(7, len(codes))
        self.assertEqual("🇮🇹 🇩🇪 🇫🇷 🇪🇸 🇵🇱", render_country_flags(["IT", *codes]))
        self.assertEqual("", render_country_flags([]))


if __name__ == "__main__":
    unittest.main()
