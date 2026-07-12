from matcher.weights import OBJECT_TYPE_WEIGHT


class ObjectTypeEvaluator:

    def evaluate(
        self,
        old_object,
        new_object,
        result
    ):

        if old_object.object_type == new_object.object_type:

            result.object_type_score = OBJECT_TYPE_WEIGHT

        else:

            result.object_type_score = 0