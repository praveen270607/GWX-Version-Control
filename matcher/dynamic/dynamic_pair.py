class DynamicPair:

    def __init__(
        self,
        old_dynamic=None,
        new_dynamic=None
    ):

        self.old_dynamic = old_dynamic

        self.new_dynamic = new_dynamic

        self.match_result = None

    def has_old(self):

        return self.old_dynamic is not None

    def has_new(self):

        return self.new_dynamic is not None

    def is_added(self):

        return (
            self.old_dynamic is None
            and self.new_dynamic is not None
        )

    def is_removed(self):

        return (
            self.old_dynamic is not None
            and self.new_dynamic is None
        )

    def is_matched(self):

        return (
            self.old_dynamic is not None
            and self.new_dynamic is not None
        )

    def set_match_result(self, result):

        self.match_result = result