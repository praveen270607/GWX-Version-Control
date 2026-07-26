import unittest
from matcher.evaluators.appearance_evaluator import AppearanceEvaluator
from matcher.match_result import MatchResult
from models import DisplayObject


class TestAppearanceEvaluator(unittest.TestCase):

    def setUp(self):
        self.evaluator = AppearanceEvaluator()

    def create_object(self, properties):
        obj = DisplayObject()
        obj.properties = properties
        return obj

    def evaluate(self, old_properties, new_properties):
        old_object = self.create_object(old_properties)
        new_object = self.create_object(new_properties)

        result = MatchResult()

        self.evaluator.evaluate(
            old_object,
            new_object,
            result
        )

        return result.appearance_score

    def test_same_appearance(self):

        score = self.evaluate(

            {
                "Fill": "Red",
                "Stroke": "Black",
                "Opacity": "1",
                "Visibility": "Visible"
            },

            {
                "Fill": "Red",
                "Stroke": "Black",
                "Opacity": "1",
                "Visibility": "Visible"
            }
        )
        self.assertEqual(score, 20)


if __name__ == "__main__":
    unittest.main()