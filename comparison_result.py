class ComparisonResult:

    def __init__(self):

        self.pairs = []
        self.added = []
        self.removed = []
        self.modified = []
        self.unchanged = []

    def add_pair(self, pair):
        self.pairs.append(pair)

    def add_added(self, obj):
        self.added.append(obj)

    def add_removed(self, obj):
        self.removed.append(obj)

    def add_modified(self, obj):
        self.modified.append(obj)

    def add_unchanged(self, obj):
        self.unchanged.append(obj)

    def to_dict(self):

        return {

            "pairs": len(self.pairs),
            "added": self.added,
            "removed": self.removed,
            "modified": self.modified,
            "unchanged": self.unchanged

        }