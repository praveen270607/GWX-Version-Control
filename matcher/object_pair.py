class ObjectPair:

    def __init__(self, old_object=None, new_object=None):

        self.old_object = old_object
        self.new_object = new_object

        self.match_result = None

    def has_old(self):
        return self.old_object is not None

    def has_new(self):
        return self.new_object is not None

    def is_added(self):
        return self.old_object is None and self.new_object is not None

    def is_removed(self):
        return self.old_object is not None and self.new_object is None

    def is_matched(self):
        return self.old_object is not None and self.new_object is not None

    def set_match_result(self, match_result):

        self.match_result = match_result