from matcher.comparison.difference_path import DifferencePath


class ComparisonContext:

    def __init__(self):

        self.current_path = DifferencePath()

        self.differences = []

        self.options = None