from matcher.evaluators.position_evaluator import PositionEvaluator
from matcher.evaluators.size_evaluator import SizeEvaluator
from matcher.evaluators.appearance_evaluator import AppearanceEvaluator
from matcher.match_result import MatchResult
from matcher.evaluators.object_type_evaluator import ObjectTypeEvaluator
from matcher.evaluators.name_evaluator import NameEvaluator
from matcher.weights import MATCH_THRESHOLD


class ObjectMatcher:

    def __init__(self):

        self.evaluators = [
            
            ObjectTypeEvaluator(),
            NameEvaluator(),
            SizeEvaluator(),
            PositionEvaluator(),
            AppearanceEvaluator()
        ]

    def match_objects(self, old_object, new_object):

        result = MatchResult()

        # Store the objects being compared
        result.old_object = old_object
        result.new_object = new_object

        for evaluator in self.evaluators:
            evaluator.evaluate(
                old_object,
                new_object,
                result
            )

        self.calculate_total(result)

        self.determine_match(result)

        return result

    def calculate_total(self, result):

        result.total_score = (
            result.object_type_score +
            result.name_score +
            result.parent_score +
            result.position_score +
            result.size_score +
            result.dynamic_score + 
            result.command_score
        )

    def determine_match(self, result):

        if result.total_score >= MATCH_THRESHOLD:
            result.is_match = True

        else:
            result.is_match = False             