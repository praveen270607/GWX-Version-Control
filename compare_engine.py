from comparison_result import ComparisonResult

from matcher.object_pairer import ObjectPairer
from matcher.object_matcher import ObjectMatcher
from matcher.comparison.comparison_context import ComparisonContext


def compare_objects(old_objects, new_objects):
    """
    Compare the objects in two displays.
    """

    # Create the final comparison result
    comparison_result = ComparisonResult()

    # Create helper objects
    pairer = ObjectPairer()
    matcher = ObjectMatcher()

    # Generate object pairs
    pairs = pairer.create_pairs(
        old_objects,
        new_objects
    )

    # Process every pair
    for pair in pairs:

        if pair.is_matched():

            match_result = matcher.match_objects(
                pair.old_object,
                pair.new_object,
                ComparisonContext()
            )

            pair.set_match_result(match_result)

            if match_result.differences:
                comparison_result.add_modified(
                    pair.old_object.object_id
                )
            else:
                comparison_result.add_unchanged(
                    pair.old_object.object_id
                )

        elif pair.is_removed():

            comparison_result.add_removed(
                pair.old_object.object_id
            )

        elif pair.is_added():

            comparison_result.add_added(
                pair.new_object.object_id
            )

        # Always store the pair
        comparison_result.add_pair(pair)

    return comparison_result
