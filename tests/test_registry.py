from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from st_platform.tasks import TaskType
from st_platform.workflows import create_platform_service


class RegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = create_platform_service(project_root=str(ROOT))

    def test_default_tasks_exist(self) -> None:
        tasks = list(self.service.list_tasks())
        task_types = {item["task_type"] for item in tasks}
        self.assertIn(TaskType.DOMAIN_DETECTION.value, task_types)
        self.assertIn(TaskType.DECONVOLUTION.value, task_types)

    def test_algorithm_filtering_works(self) -> None:
        algorithms = list(self.service.list_algorithms(TaskType.DOMAIN_DETECTION))
        algorithm_ids = {item["algorithm_id"] for item in algorithms}
        self.assertEqual({"mock-domain"}, algorithm_ids)


if __name__ == "__main__":
    unittest.main()

