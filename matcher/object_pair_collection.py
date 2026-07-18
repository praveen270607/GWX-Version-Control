class ObjectPairCollection:

    def __init__(self):

        self.pairs = []

    def add_pair(self, pair):

        self.pairs.append(pair)

    def __iter__(self):

        return iter(self.pairs)

    def __len__(self):

        return len(self.pairs)