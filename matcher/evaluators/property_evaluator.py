class PropertyEvaluator:

    def get_properties(self):
        raise NotImplementedError(
            "Child class must implement get_properties()."
        )

    def get_weight(self):
        raise NotImplementedError(
            "Child class must implement get_weight()."
        )

    def set_score(self, result, earned_score):
        raise NotImplementedError(
            "Child class must implement set_score()."
        )

    def evaluate(
        self,
        old_object,
        new_object,
        result
    ):

        properties = self.get_properties()

        if not properties:
            return

        weight = self.get_weight()

        earned_score = 0

        score_per_property = (
            weight / len(properties)
        )

        for property_name in properties:

            old_value = old_object.properties.get(property_name)
            new_value = new_object.properties.get(property_name)

            if old_value is None or new_value is None:
                continue

            if old_value == new_value:
                earned_score += score_per_property

        self.set_score(
            result,
            earned_score
        )