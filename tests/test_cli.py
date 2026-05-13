import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from st_platform.cli import _default_parameters_for_demo
from st_platform.tasks import TaskType


class CliTests(unittest.TestCase):
    def test_spagcn_demo_uses_algorithm_specific_defaults(self) -> None:
        parameters = _default_parameters_for_demo(
            task_type=TaskType.DOMAIN_DETECTION,
            algorithm_id="spagcn",
        )

        self.assertEqual(
            {
                "n_clusters": 3,
                "neighbor_k": 3,
                "num_pcs": 2,
                "l": 1.0,
                "max_epochs": 2,
                "random_state": 0,
            },
            parameters,
        )

    def test_spagcn_lite_demo_uses_algorithm_specific_defaults(self) -> None:
        parameters = _default_parameters_for_demo(
            task_type=TaskType.DOMAIN_DETECTION,
            algorithm_id="spagcn-lite",
        )

        self.assertEqual(
            {
                "n_clusters": 3,
                "neighbor_k": 3,
                "spatial_weight": 0.25,
                "random_state": 0,
            },
            parameters,
        )

    def test_mock_domain_demo_keeps_task_defaults(self) -> None:
        parameters = _default_parameters_for_demo(
            task_type=TaskType.DOMAIN_DETECTION,
            algorithm_id="mock-domain",
        )

        self.assertEqual({"resolution": 0.8}, parameters)


if __name__ == "__main__":
    unittest.main()
