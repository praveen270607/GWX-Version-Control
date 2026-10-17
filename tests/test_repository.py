import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
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
    merge_branch,
    restore_file,
    save_index,
    show_log,
    stage_file,
    stage_remove,
    status,
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

    def test_files_have_independent_versions_and_global_commit_ids(self):

        stage_file(self.display, self.root)
        commit("Add pump display", self.root)

        self.assertEqual(get_branch_head(root=self.root), "000001")
        initial_tree = current_tree(self.root)
        self.assertEqual(initial_tree["Displays/Pump.gdfx"]["file_revision"], 1)
        self.assertEqual(initial_tree["Displays/Pump.gdfx"]["last_commit"], "000001")

        valve = self.root / "Symbols" / "Valve.sdfx"
        valve.parent.mkdir()
        valve.write_text("valve version one", encoding="utf-8")
        stage_file(valve, self.root)
        commit("Add valve symbol", self.root)

        tree_after_symbol = current_tree(self.root)
        self.assertEqual(tree_after_symbol["Displays/Pump.gdfx"]["file_revision"], 1)
        self.assertEqual(tree_after_symbol["Symbols/Valve.sdfx"]["file_revision"], 1)
        self.assertEqual(tree_after_symbol["Symbols/Valve.sdfx"]["last_commit"], "000002")

        self.display.write_text("version two", encoding="utf-8")
        stage_file(self.display, self.root)
        commit("Update pump display", self.root)

        updated_tree = current_tree(self.root)
        self.assertEqual(get_branch_head(root=self.root), "000003")
        self.assertEqual(updated_tree["Displays/Pump.gdfx"]["file_revision"], 2)
        self.assertEqual(updated_tree["Symbols/Valve.sdfx"]["file_revision"], 1)
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
        with self.assertRaisesRegex(RepositoryError, "base file version is no longer current"):
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

    def test_checkout_restores_branch_version_and_protects_dirty_file(self):

        stage_file(self.display, self.root)
        commit("Add pump display", self.root)
        create_branch("feature", self.root)

        self.display.write_text("uncommitted", encoding="utf-8")
        with self.assertRaisesRegex(RepositoryError, "uncommitted changes"):
            checkout_branch("feature", self.root)

        restore_file(self.display, self.root)
        checkout_branch("feature", self.root)
        self.assertEqual(self.display.read_text(encoding="utf-8"), "version one")

    def test_fast_forward_merge_restores_the_newer_file(self):

        stage_file(self.display, self.root)
        commit("Add pump display", self.root)
        create_branch("feature", self.root)
        checkout_branch("feature", self.root)

        self.display.write_text("feature version", encoding="utf-8")
        stage_file(self.display, self.root)
        commit("Feature update", self.root)

        checkout_branch("main", self.root)
        merge_branch("feature", self.root)

        self.assertEqual(get_branch_head(root=self.root), "000002")
        self.assertEqual(self.display.read_text(encoding="utf-8"), "feature version")

    def test_merge_rejects_two_changes_to_the_same_file(self):

        stage_file(self.display, self.root)
        commit("Add pump display", self.root)
        create_branch("feature", self.root)
        checkout_branch("feature", self.root)

        self.display.write_text("feature version", encoding="utf-8")
        stage_file(self.display, self.root)
        commit("Feature update", self.root)

        checkout_branch("main", self.root)
        self.display.write_text("main version", encoding="utf-8")
        stage_file(self.display, self.root)
        commit("Main update", self.root)

        with self.assertRaisesRegex(RepositoryError, "both branches changed"):
            merge_branch("feature", self.root)

    def test_commit_can_remove_a_tracked_file(self):

        stage_file(self.display, self.root)
        commit("Add pump display", self.root)
        stage_remove(self.display, self.root)
        self.assertFalse(self.display.exists())
        commit("Remove pump display", self.root)

        self.assertNotIn("Displays/Pump.gdfx", current_tree(self.root))

    def test_status_and_log_show_file_versions(self):

        stage_file(self.display, self.root)
        commit("Add pump display", self.root)

        output = StringIO()
        with redirect_stdout(output):
            status(self.root)
            show_log(self.root)

        rendered = output.getvalue()
        self.assertIn("file version: 1", rendered)
        self.assertIn("last commit: 000001", rendered)
        self.assertIn("add: Displays/Pump.gdfx (file version - -> 1)", rendered)


if __name__ == "__main__":
    unittest.main()
