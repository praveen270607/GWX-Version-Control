from matcher.evaluators.property_evaluator import PropertyEvaluator
from matcher.graphworkx_property_groups import APPEARANCE_PROPERTIES
from matcher.weights import APPEARANCE_WEIGHT


class AppearanceEvaluator(PropertyEvaluator):

    def get_properties(self):
        return APPEARANCE_PROPERTIES

    def get_weight(self):
        return APPEARANCE_WEIGHT

    def set_score(
        self,
        result,
        earned_score
    ):
        result.appearance_score = earned_score