from matcher.weights import NAME_WEIGHT


class NameEvaluator:

    def evaluate(self, old_object, new_object, result):

        # If either object has no name,
        # don't use the name as evidence.

        if not old_object.name or not new_object.name:
            return

        if old_object.name == new_object.name:
            result.name_score = NAME_WEIGHT