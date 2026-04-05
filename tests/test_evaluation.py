import unittest
from pathlib import Path

from data_platform_copilot.evaluation import evaluate


class EvaluationTests(unittest.TestCase):
    def test_evaluation_runs(self) -> None:
        output = evaluate(Path("data/corpus"), Path("data/eval/cases.json"))

        self.assertIn("Evaluation results", output)
        self.assertIn("billing-failure-root-cause", output)


if __name__ == "__main__":
    unittest.main()
