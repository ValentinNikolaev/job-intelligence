from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from jobintel.workflow_lock import (
    LOCK_ENV_TOKEN,
    WorkflowLockError,
    acquire_workflow_lock,
    workflow_lock,
    workflow_lock_status,
)


class WorkflowLockTests(unittest.TestCase):
    def test_lock_excludes_second_owner_until_released(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            lease = acquire_workflow_lock(root, "collection")
            self.assertTrue(workflow_lock_status(root)["locked"])

            with self.assertRaises(WorkflowLockError):
                acquire_workflow_lock(root, "analysis")

            lease.release()
            self.assertFalse(workflow_lock_status(root)["locked"])

            acquire_workflow_lock(root, "analysis").release()

    def test_existing_token_allows_nested_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            lease = acquire_workflow_lock(root, "analysis")
            old_token = os.environ.get(LOCK_ENV_TOKEN)
            os.environ[LOCK_ENV_TOKEN] = lease.token
            try:
                with workflow_lock(root, "analysis:pack") as nested:
                    self.assertFalse(nested.acquired)
                self.assertTrue(workflow_lock_status(root)["locked"])
            finally:
                if old_token is None:
                    os.environ.pop(LOCK_ENV_TOKEN, None)
                else:
                    os.environ[LOCK_ENV_TOKEN] = old_token
                lease.release()


if __name__ == "__main__":
    unittest.main()
