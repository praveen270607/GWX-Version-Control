from matcher.comparison.difference_level import DifferenceLevel
from matcher.comparison.difference_path import DifferencePath
from matcher.comparison.difference_type import DifferenceType


class Difference:
    """
    Represents a single difference found during comparison.
    """

    def __init__(
        self,
        level: DifferenceLevel,
        difference_type: DifferenceType,
        path: DifferencePath,
        old_value=None,
        new_value=None
    ):

        self.level = level
        self.difference_type = difference_type
        self.path = path

        self.old_value = old_value
        self.new_value = new_value

    def __str__(self):

        return (
            f"{self.difference_type.value} "
            f"{self.level.value} "
            f"at {self.path} "
            f"({self.format_value(self.old_value)} -> "
            f"{self.format_value(self.new_value)})"
        )

    @staticmethod
    def format_value(value):

        if value is None:
            return "None"

        value = str(value)

        if len(value) <= 120:
            return value

        return f"{value[:117]}..."
