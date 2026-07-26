from matcher.evaluators.property_evaluator import PropertyEvaluator
from matcher.graphworkx_property_groups import SIZE_PROPERTIES
from matcher.weights import SIZE_WEIGHT


class SizeEvaluator(PropertyEvaluator):

    def get_properties(self):
        return SIZE_PROPERTIES

    def get_weight(self):
        return SIZE_WEIGHT

    def set_score(
        self,
        result,
        earned_score
    ):
        result.size_score = earned_score