import unittest
from pathlib import Path

from data_platform_copilot.agent import DataPlatformCopilot


class AgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.copilot = DataPlatformCopilot(Path("data/corpus"))

    def test_failure_question_returns_expected_citations(self) -> None:
        answer = self.copilot.ask("Why did yesterday's pipeline fail?")

        self.assertIn("incident_2026_04_04_billing_failure", answer.citations)
        self.assertIn("pipeline_run_2026_04_04", answer.citations)
        self.assertTrue(any("schema" in cause.lower() for cause in answer.likely_root_causes))

    def test_row_count_question_mentions_mismatches(self) -> None:
        answer = self.copilot.ask("Which tables had row-count mismatches this week?")

        self.assertIn("billing_fact", answer.answer.lower())
        self.assertIn("customer_dim", answer.answer.lower())


if __name__ == "__main__":
    unittest.main()
