class DifferencePath:

    def __init__(self):

        self.segments = []

    def add(self, segment):

        self.segments.append(segment)

    def remove_last(self):

        if self.segments:
            self.segments.pop()

    def clear(self):

        self.segments.clear()

    def copy(self):

        new_path = DifferencePath()

        new_path.segments = self.segments.copy()

        return new_path

    def __len__(self):

        return len(self.segments)

    def __str__(self):

        return "/".join(self.segments)