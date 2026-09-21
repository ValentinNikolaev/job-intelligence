from __future__ import annotations

import unittest

from jobintel.storage_contract import SourceIdentityConflict


class StorageContractTests(unittest.TestCase):
    def test_source_identity_conflict_keeps_both_vacancy_ids(self) -> None:
        error = SourceIdentityConflict("adzuna", "job-1", "existing", "incoming")

        self.assertEqual("existing", error.existing_vacancy_id)
        self.assertEqual("incoming", error.incoming_vacancy_id)
        self.assertIn("adzuna:job-1", str(error))


if __name__ == "__main__":
    unittest.main()
