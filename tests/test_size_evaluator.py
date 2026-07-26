import unittest

from matcher.evaluators.size_evaluator import SizeEvaluator
from matcher.match_result import MatchResult
from models import DisplayObject


class TestSizeEvaluator(unittest.TestCase):

    def setUp(self):
        self.evaluator = SizeEvaluator()

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

        return result.size_score

    def test_same_size(self):
        score = self.evaluate(
            {
                "Width": "100",
                "Height": "50"
            },
            {
                "Width": "100",
                "Height": "50"
            }
        )

        self.assertEqual(score, 20)

    def test_width_changed(self):
        score = self.evaluate(
            {
                "Width": "100",
                "Height": "50"
            },
            {
                "Width": "120",
                "Height": "50"
            }
        )

        self.assertEqual(score, 10)

    def test_both_changed(self):
        score = self.evaluate(
            {
                "Width": "100",
                "Height": "50"
            },
            {
                "Width": "120",
                "Height": "80"
            }
        )

        self.assertEqual(score, 0)

    def test_missing_height(self):
        score = self.evaluate(
            {
                "Width": "100",
                "Height": "50"
            },
            {
                "Width": "100"
            }
        )

        self.assertEqual(score, 10)


if __name__ == "__main__":
    unittest.main()