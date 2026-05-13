import json
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
SPAGCN_AVAILABLE = importlib.util.find_spec("SpaGCN") is not None

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

    def test_spagcn_lite_domain_detection_writes_assignments(self) -> None:
        result = self.service.run(
            task_type=TaskType.DOMAIN_DETECTION,
            algorithm_id="spagcn-lite",
            data=self.demo_data,
            parameters={"n_clusters": 3, "neighbor_k": 3, "random_state": 7},
        )

        self.assertEqual(RunStatus.SUCCEEDED, result.status)
        self.assertEqual("spagcn-lite", result.algorithm_id)
        self.assertEqual(3, result.summary["predicted_domains"])
        self.assertEqual(
            self.demo_data.metadata["spot_count"],
            result.metrics["spot_count"],
        )
        self.assertGreaterEqual(result.metrics["spatial_neighbor_agreement"], 0.0)
        self.assertLessEqual(result.metrics["spatial_neighbor_agreement"], 1.0)

        artifact = result.artifacts[0]
        self.assertEqual("domain_assignments", artifact["kind"])
        assignment_path = Path(artifact["uri"])
        self.assertTrue(assignment_path.exists())
        assignments = json.loads(assignment_path.read_text(encoding="utf-8"))
        self.assertEqual(
            self.demo_data.metadata["spot_count"],
            len(assignments["domains"]),
        )

    @unittest.skipUnless(SPAGCN_AVAILABLE, "SpaGCN dependencies are not installed")
    def test_spagcn_domain_detection_runs_real_backend(self) -> None:
        result = self.service.run(
            task_type=TaskType.DOMAIN_DETECTION,
            algorithm_id="spagcn",
            data=self.demo_data,
            parameters={
                "n_clusters": 3,
                "num_pcs": 2,
                "l": 1.0,
                "max_epochs": 2,
                "random_state": 11,
            },
        )

        self.assertEqual(RunStatus.SUCCEEDED, result.status)
        self.assertEqual("spagcn", result.algorithm_id)
        self.assertEqual("SpaGCN", result.summary["backend"])
        self.assertEqual(3, result.summary["predicted_domains"])

        artifact = result.artifacts[0]
        self.assertEqual("domain_assignments", artifact["kind"])
        assignments = json.loads(Path(artifact["uri"]).read_text(encoding="utf-8"))
        self.assertEqual("spagcn", assignments["algorithm_id"])
        self.assertEqual(
            self.demo_data.metadata["spot_count"],
            len(assignments["domains"]),
        )


if __name__ == "__main__":
    unittest.main()

