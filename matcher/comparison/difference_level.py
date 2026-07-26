from enum import Enum


class DifferenceLevel(Enum):
    """
    Represents the level where a difference occurred.
    """

    OBJECT = "Object"
    PROPERTY = "Property"
    DYNAMIC = "Dynamic"
    COMMAND = "Command"
    PARAMETER = "Parameter"