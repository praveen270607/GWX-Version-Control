from matcher.evaluators.position_evaluator import PositionEvaluator
from matcher.evaluators.size_evaluator import SizeEvaluator
from matcher.evaluators.appearance_evaluator import AppearanceEvaluator
from matcher.match_result import MatchResult
from matcher.evaluators.object_type_evaluator import ObjectTypeEvaluator
from matcher.evaluators.name_evaluator import NameEvaluator
from matcher.weights import MATCH_THRESHOLD
from matcher.dynamic.dynamic_matcher import DynamicMatcher
from matcher.comparison.comparison_context import ComparisonContext
from matcher.comparison.difference import Difference
from matcher.comparison.difference_level import DifferenceLevel
from matcher.comparison.difference_type import DifferenceType


class ObjectMatcher:

    def __init__(self):

        self.evaluators = [
            
            ObjectTypeEvaluator(),
            NameEvaluator(),
            SizeEvaluator(),
            PositionEvaluator(),
            AppearanceEvaluator()
        ]

    def match_objects(self, old_object, new_object, context=None):

        result = MatchResult()

        # Store the objects being compared
        result.old_object = old_object
        result.new_object = new_object

        if context is None:
            context = ComparisonContext()

        context.current_path.push(old_object.object_id)

        self.compare_properties(old_object, new_object, context, result)

        dynamic_result = DynamicMatcher().match(
            old_object.dynamics,
            new_object.dynamics,
            context
        )
        result.differences.extend(dynamic_result.differences)

        for evaluator in self.evaluators:
            evaluator.evaluate(
                old_object,
                new_object,
                result
            )

        self.calculate_total(result)

        self.determine_match(result)

        context.current_path.pop()

        return result

    def compare_properties(self, old_object, new_object, context, result):

        for property_name in sorted(
            set(old_object.properties) | set(new_object.properties)
        ):

            old_value = old_object.properties.get(property_name)
            new_value = new_object.properties.get(property_name)

            if old_value == new_value:
                continue

            if old_value is None:
                difference_type = DifferenceType.ADDED
            elif new_value is None:
                difference_type = DifferenceType.REMOVED
            else:
                difference_type = DifferenceType.MODIFIED

            context.current_path.push(property_name)

            difference = Difference(
                level=DifferenceLevel.PROPERTY,
                difference_type=difference_type,
                path=context.current_path.copy(),
                old_value=old_value,
                new_value=new_value
            )

            result.changed_properties.append(property_name)
            result.differences.append(difference)

            context.current_path.pop()

    def calculate_total(self, result):

        result.total_score = (
            result.object_type_score +
            result.name_score +
            result.parent_score +
            result.position_score +
            result.size_score +
            result.appearance_score +
            result.dynamic_score + 
            result.command_score
        )

    def determine_match(self, result):

        if result.total_score >= MATCH_THRESHOLD:
            result.is_match = True

        else:
            result.is_match = False
