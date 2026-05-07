from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from st_platform.core import RunStatus
from st_platform.tasks import TaskType
from st_platform.workflows import create_platform_service


class RunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = create_platform_service(project_root=str(ROOT))
        self.demo_data = self.service.build_demo_dataset()

    def test_domain_detection_demo_succeeds(self) -> None:
        result = self.service.run(
            task_type=TaskType.DOMAIN_DETECTION,
            algorithm_id="mock-domain",
            data=self.demo_data,
            parameters={"resolution": 0.6},
        )
        self.assertEqual(RunStatus.SUCCEEDED, result.status)
        self.assertEqual("mock-domain", result.algorithm_id)
        self.assertIn("predicted_domains", result.summary)

    def test_task_algorithm_mismatch_fails(self) -> None:
        result = self.service.run(
            task_type=TaskType.DECONVOLUTION,
            algorithm_id="mock-domain",
            data=self.demo_data,
            parameters={},
        )
        self.assertEqual(RunStatus.FAILED, result.status)
        self.assertIsNotNone(result.error)


if __name__ == "__main__":
    unittest.main()

