import unittest

from matcher.comparison.comparison_context import ComparisonContext
from matcher.dynamic.dynamic_matcher import DynamicMatcher
from models import CommandObject, DynamicObject


def make_dynamic(dynamic_type, properties=None, commands=None):

    dynamic = DynamicObject()
    dynamic.dynamic_type = dynamic_type
    dynamic.properties = properties or {}
    dynamic.commands = commands or []

    return dynamic


def make_command(command_type, properties=None, parameters=None):

    command = CommandObject()
    command.command_type = command_type
    command.properties = properties or {}
    command.parameters = parameters or {}

    return command


class TestDynamicMatcher(unittest.TestCase):

    def test_pairs_and_reports_added_removed_dynamics(self):

        result = DynamicMatcher().match(
            [make_dynamic("Pick"), make_dynamic("Hide")],
            [make_dynamic("Pick"), make_dynamic("Rotation")],
            ComparisonContext()
        )

        self.assertEqual(len(result.pairs), 3)
        self.assertEqual(
            [str(difference) for difference in result.differences],
            [
                "Removed Dynamic at Hide (Hide -> None)",
                "Added Dynamic at Rotation (None -> Rotation)"
            ]
        )

    def test_reports_dynamic_and_command_parameter_changes(self):

        old_dynamic = make_dynamic(
            "GwxPick",
            {"ExecuteOnUp": "True"},
            [make_command("LoadDisplayCommand", {"Target": "A"})]
        )
        new_dynamic = make_dynamic(
            "GwxPick",
            {"ExecuteOnUp": "False"},
            [
                make_command("LoadDisplayCommand", {"Target": "B"}),
                make_command("WriteValueCommand")
            ]
        )

        result = DynamicMatcher().match(
            [old_dynamic],
            [new_dynamic],
            ComparisonContext()
        )

        self.assertEqual(len(result.pairs), 1)
        self.assertEqual(
            len(result.pairs[0].match_result.differences),
            3
        )
        self.assertEqual(
            [str(difference) for difference in result.differences],
            [
                "Modified Property at GwxPick/ExecuteOnUp (True -> False)",
                "Modified Parameter at GwxPick/LoadDisplayCommand/Target (A -> B)",
                "Added Command at GwxPick/WriteValueCommand (None -> WriteValueCommand)"
            ]
        )


if __name__ == "__main__":
    unittest.main()
