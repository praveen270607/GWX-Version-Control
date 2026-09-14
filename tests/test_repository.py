import tempfile
import unittest
from pathlib import Path

from repository import (
    RepositoryError,
    checkout_branch,
    commit,
    create_branch,
    current_tree,
    get_branch_head,
    initialize_repository,
    load_index,
    save_index,
    stage_file,
)


class TestRepositoryWorkflow(unittest.TestCase):

    def setUp(self):
        workspace = Path(__file__).resolve().parent.parent
        self.temporary_directory = tempfile.TemporaryDirectory(dir=workspace)
        self.root = Path(self.temporary_directory.name)
        self.display = self.root / "Displays" / "Pump.gdfx"
        self.display.parent.mkdir()
        self.display.write_text("version one", encoding="utf-8")
        initialize_repository(self.root)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_commit_stores_immutable_file_and_advances_revision(self):

        stage_file(self.display, self.root)
        commit("Add pump display", self.root)

        self.assertEqual(get_branch_head(root=self.root), "000001")
        initial_tree = current_tree(self.root)
        self.assertEqual(initial_tree["Displays/Pump.gdfx"]["revision"], "000001")

        self.display.write_text("version two", encoding="utf-8")
        stage_file(self.display, self.root)
        commit("Update pump display", self.root)

        updated_tree = current_tree(self.root)
        self.assertEqual(updated_tree["Displays/Pump.gdfx"]["revision"], "000002")
        self.assertNotEqual(
            initial_tree["Displays/Pump.gdfx"]["blob"],
            updated_tree["Displays/Pump.gdfx"]["blob"]
        )

    def test_rejects_a_staged_change_when_its_base_revision_is_stale(self):

        stage_file(self.display, self.root)
        commit("Add pump display", self.root)
        self.display.write_text("first editor version", encoding="utf-8")
        stage_file(self.display, self.root)
        stale_index = load_index(self.root)
        staged_feature_blob = stale_index["Displays/Pump.gdfx"]["new_blob"]

        self.display.write_text("second editor version", encoding="utf-8")
        stage_file(self.display, self.root)
        commit("Second editor update", self.root)

        save_index(stale_index, self.root)
        with self.assertRaisesRegex(RepositoryError, "base revision is no longer current"):
            commit("First editor update", self.root)

        self.assertEqual(
            load_index(self.root)["Displays/Pump.gdfx"]["new_blob"],
            staged_feature_blob
        )

    def test_branch_has_an_independent_head(self):

        stage_file(self.display, self.root)
        commit("Add pump display", self.root)
        create_branch("feature", self.root)

        checkout_branch("feature", self.root)
        self.display.write_text("feature version", encoding="utf-8")
        stage_file(self.display, self.root)
        commit("Feature update", self.root)

        self.assertEqual(get_branch_head(root=self.root), "000002")

        checkout_branch("main", self.root)
        self.assertEqual(get_branch_head(root=self.root), "000001")


if __name__ == "__main__":
    unittest.main()
