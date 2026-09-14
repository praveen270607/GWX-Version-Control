class DynamicMatchResult:

    def __init__(self):

        self.structure_score = 0

        self.command_score = 0

        self.parameter_score = 0

        self.total_score = 0

        self.differences = []

        self.pairs = []

    def calculate_total(self):

        self.total_score = (
            self.structure_score +
            self.command_score +
            self.parameter_score
        )

    def add_difference(self, difference):

        self.differences.append(difference)

    def add_pair(self, pair):

        self.pairs.append(pair)