from matcher.evaluators.property_evaluator import PropertyEvaluator
from matcher.graphworkx_property_groups import POSITION_PROPERTIES
from matcher.weights import POSITION_WEIGHT


class PositionEvaluator(PropertyEvaluator):

    def get_properties(self):
        return POSITION_PROPERTIES

    def get_weight(self):
        return POSITION_WEIGHT

    def set_score(
        self,
        result,
        earned_score
    ):
        result.position_score = earned_score