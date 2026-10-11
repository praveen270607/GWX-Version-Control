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

                    pair = DynamicPair(old_dynamic, new_dynamic)

                    self.compare_matched_dynamic(
                        pair,
                        context,
                        result
                    )

                    result.add_pair(pair)

                    matched = True

                    break

            if not matched:

                result.add_pair(DynamicPair(old_dynamic, None))

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

                result.add_pair(DynamicPair(None, new_dynamic))

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

    def compare_matched_dynamic(self, pair, context, result):

        dynamic_type = pair.old_dynamic.dynamic_type

        pair_result = DynamicMatchResult()

        context.current_path.push(dynamic_type)

        self.compare_values(
            pair.old_dynamic.properties,
            pair.new_dynamic.properties,
            DifferenceLevel.PROPERTY,
            context,
            pair_result
        )

        self.compare_commands(
            pair.old_dynamic.commands,
            pair.new_dynamic.commands,
            context,
            pair_result
        )

        context.current_path.pop()

        pair.set_match_result(pair_result)

        result.differences.extend(pair_result.differences)

    def compare_commands(self, old_commands, new_commands, context, result):

        matched_new_indexes = set()

        for old_command in old_commands:

            match_index = next(
                (
                    index
                    for index, new_command in enumerate(new_commands)
                    if index not in matched_new_indexes
                    and old_command.command_type == new_command.command_type
                ),
                None
            )

            if match_index is None:
                self.add_difference(
                    DifferenceLevel.COMMAND,
                    DifferenceType.REMOVED,
                    old_command.command_type,
                    old_command.command_type,
                    None,
                    context,
                    result
                )
                continue

            matched_new_indexes.add(match_index)

            new_command = new_commands[match_index]

            context.current_path.push(old_command.command_type)

            self.compare_values(
                old_command.properties,
                new_command.properties,
                DifferenceLevel.PARAMETER,
                context,
                result
            )
            self.compare_values(
                old_command.parameters,
                new_command.parameters,
                DifferenceLevel.PARAMETER,
                context,
                result
            )

            context.current_path.pop()

        for index, new_command in enumerate(new_commands):

            if index not in matched_new_indexes:
                self.add_difference(
                    DifferenceLevel.COMMAND,
                    DifferenceType.ADDED,
                    new_command.command_type,
                    None,
                    new_command.command_type,
                    context,
                    result
                )

    def compare_values(self, old_values, new_values, level, context, result):

        for key in sorted(set(old_values) | set(new_values)):

            old_value = old_values.get(key)
            new_value = new_values.get(key)

            if old_value != new_value:

                if old_value is None:
                    difference_type = DifferenceType.ADDED
                elif new_value is None:
                    difference_type = DifferenceType.REMOVED
                else:
                    difference_type = DifferenceType.MODIFIED

                self.add_difference(
                    level,
                    difference_type,
                    key,
                    old_value,
                    new_value,
                    context,
                    result
                )

    def add_difference(
        self,
        level,
        difference_type,
        segment,
        old_value,
        new_value,
        context,
        result
    ):

        context.current_path.push(segment)

        difference = Difference(
            level=level,
            difference_type=difference_type,
            path=context.current_path.copy(),
            old_value=old_value,
            new_value=new_value
        )

        result.add_difference(difference)

        context.current_path.pop()
