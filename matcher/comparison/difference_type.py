from enum import Enum


class DifferenceType(Enum):
    """
    Represents the type of change detected during comparison.
    """

    ADDED = "Added"
    REMOVED = "Removed"
    MODIFIED = "Modified"
    MOVED = "Moved"