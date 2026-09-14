from matcher.comparison.difference import Difference
from matcher.comparison.difference_level import DifferenceLevel
from matcher.comparison.difference_type import DifferenceType
from matcher.dynamic.dynamic_match_result import DynamicMatchResult
from matcher.dynamic.dynamic_pair import DynamicPair


class DynamicMatcher:

    def match(self, old_dynamics, new_dynamics, context):

        result = DynamicMatchResult()

        matched_new_indexes = set()

        for old_dynamic in old_dynamics:

            matched = False

            for index, new_dynamic in enumerate(new_dynamics):

                if index in matched_new_indexes:
                    continue

                if old_dynamic.dynamic_type == new_dynamic.dynamic_type:

                    matched_new_indexes.add(index)

                    matched = True

                    break

            if not matched:

                context.current_path.push(
                    old_dynamic.dynamic_type
                )

                difference = Difference(
                    level=DifferenceLevel.DYNAMIC,
                    difference_type=DifferenceType.REMOVED,
                    path=context.current_path.copy(),
                    old_value=old_dynamic.dynamic_type,
                    new_value=None
                )

                result.add_difference(difference)

                context.current_path.pop()

        for index, new_dynamic in enumerate(new_dynamics):

            if index not in matched_new_indexes:

                context.current_path.push(
                    new_dynamic.dynamic_type
                )

                difference = Difference(
                    level=DifferenceLevel.DYNAMIC,
                    difference_type=DifferenceType.ADDED,
                    path=context.current_path.copy(),
                    old_value=None,
                    new_value=new_dynamic.dynamic_type
                )

                result.add_difference(difference)

                context.current_path.pop()

        return result