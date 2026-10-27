

import unittest

from predictor import predict_student


class TestPredictor(unittest.TestCase):

    def setUp(self):
        self.student = {
            "Gender": "Female",
            "Study_Hours_per_Week": 15,
            "Attendance_Rate": 85.0,
            "Past_Exam_Scores": 70,
            "Parental_Education_Level": "Bachelors",
            "Internet_Access_at_Home": "Yes",
            "Extracurricular_Activities": "Yes",
        }

    def test_prediction_returns_valid_status(self):
        result = predict_student(self.student)

        self.assertIn(
            result["predicted_status"],
            ["Pass", "Fail"]
        )

    def test_probabilities_are_valid(self):
        result = predict_student(self.student)
        probabilities = result["probabilities"]

        self.assertIn("Pass", probabilities)
        self.assertIn("Fail", probabilities)

        for probability in probabilities.values():
            self.assertGreaterEqual(probability, 0)
            self.assertLessEqual(probability, 1)

        self.assertAlmostEqual(
            sum(probabilities.values()),
            1.0,
            places=5
        )

    def test_missing_feature_is_rejected(self):
        incomplete_student = self.student.copy()
        del incomplete_student["Gender"]

        with self.assertRaises(ValueError):
            predict_student(incomplete_student)


if __name__ == "__main__":
    unittest.main()
