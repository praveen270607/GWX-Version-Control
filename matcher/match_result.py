class MatchResult:
    """
    Stores the result of comparing two objects.
    """

    def __init__(self):

        # Final result
        self.is_match = False

        # Total score (0-100)
        self.total_score = 0

        # Individual scores
        self.object_type_score = 0
        self.name_score = 0
        self.parent_score = 0
        self.position_score = 0
        self.size_score = 0
        self.dynamic_score = 0
        self.command_score = 0

        # References
        self.old_object = None
        self.new_object = None

    def to_dict(self):

        return {

            "is_match": self.is_match,

            "total_score": self.total_score,

            "object_type_score": self.object_type_score,

            "name_score": self.name_score,

            "parent_score": self.parent_score,

            "position_score": self.position_score,

            "size_score": self.size_score,

            "dynamic_score": self.dynamic_score,

            "command_score": self.command_score
        }