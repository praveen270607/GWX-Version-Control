from matcher.dynamic.dynamic_matcher import DynamicMatcher
from matcher.comparison.comparison_context import ComparisonContext


class FakeDynamic:

    def __init__(self, dynamic_type):

        self.dynamic_type = dynamic_type


def test_dynamic_matching():

    old_dynamics = [

        FakeDynamic("Pick"),
        FakeDynamic("Hide"),
        FakeDynamic("Color")

    ]

    new_dynamics = [

        FakeDynamic("Pick"),
        FakeDynamic("Color"),
        FakeDynamic("Rotation")

    ]

    context = ComparisonContext()

    context.current_path.push("Rectangle1")

    matcher = DynamicMatcher()

    result = matcher.match(
        old_dynamics,
        new_dynamics,
        context
    )

    for difference in result.differences:

        print(
            difference.difference_type.value,
            difference.level.value,
            difference.path,
            difference.old_value,
            difference.new_value
        )


if __name__ == "__main__":

    test_dynamic_matching()