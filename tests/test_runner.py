import json
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
SPAGCN_AVAILABLE = importlib.util.find_spec("SpaGCN") is not None
GRAPHST_AVAILABLE = importlib.util.find_spec("GraphST") is not None
SEDR_AVAILABLE = importlib.util.find_spec("SEDR") is not None
TORCH_AVAILABLE = importlib.util.find_spec("torch") is not None
PYG_AVAILABLE = importlib.util.find_spec("torch_geometric") is not None

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

    @unittest.skipUnless(GRAPHST_AVAILABLE, "GraphST dependencies are not installed")
    def test_graphst_domain_detection_runs_real_backend(self) -> None:
        result = self.service.run(
            task_type=TaskType.DOMAIN_DETECTION,
            algorithm_id="graphst",
            data=self.demo_data,
            parameters={
                "n_clusters": 3,
                "epochs": 2,
                "dim_output": 4,
                "random_state": 13,
            },
        )

        self.assertEqual(RunStatus.SUCCEEDED, result.status)
        self.assertEqual("graphst", result.algorithm_id)
        self.assertEqual("GraphST", result.summary["backend"])
        self.assertEqual(3, result.summary["predicted_domains"])

        assignments = json.loads(
            Path(result.artifacts[0]["uri"]).read_text(encoding="utf-8")
        )
        self.assertEqual("graphst", assignments["algorithm_id"])
        self.assertEqual(
            self.demo_data.metadata["spot_count"],
            len(assignments["domains"]),
        )

    @unittest.skipUnless(SEDR_AVAILABLE, "SEDR dependencies are not installed")
    def test_sedr_domain_detection_runs_real_backend(self) -> None:
        result = self.service.run(
            task_type=TaskType.DOMAIN_DETECTION,
            algorithm_id="sedr",
            data=self.demo_data,
            parameters={
                "n_clusters": 3,
                "epochs": 2,
                "neighbor_k": 3,
                "random_state": 17,
            },
        )

        self.assertEqual(RunStatus.SUCCEEDED, result.status)
        self.assertEqual("sedr", result.algorithm_id)
        self.assertEqual("SEDR", result.summary["backend"])
        self.assertEqual(3, result.summary["predicted_domains"])

        assignments = json.loads(
            Path(result.artifacts[0]["uri"]).read_text(encoding="utf-8")
        )
        self.assertEqual("sedr", assignments["algorithm_id"])
        self.assertEqual(
            self.demo_data.metadata["spot_count"],
            len(assignments["domains"]),
        )

    @unittest.skipUnless(PYG_AVAILABLE, "CCST dependencies are not installed")
    def test_ccst_domain_detection_runs_real_backend(self) -> None:
        result = self.service.run(
            task_type=TaskType.DOMAIN_DETECTION,
            algorithm_id="ccst",
            data=self.demo_data,
            parameters={
                "n_clusters": 3,
                "epochs": 2,
                "hidden": 4,
                "neighbor_k": 3,
                "random_state": 19,
            },
        )

        self.assertEqual(RunStatus.SUCCEEDED, result.status)
        self.assertEqual("ccst", result.algorithm_id)
        self.assertEqual("CCST", result.summary["backend"])
        self.assertEqual(3, result.summary["predicted_domains"])

        assignments = json.loads(
            Path(result.artifacts[0]["uri"]).read_text(encoding="utf-8")
        )
        self.assertEqual("ccst", assignments["algorithm_id"])
        self.assertEqual(
            self.demo_data.metadata["spot_count"],
            len(assignments["domains"]),
        )

    @unittest.skipUnless(TORCH_AVAILABLE, "conST dependencies are not installed")
    def test_const_domain_detection_runs_model_backend(self) -> None:
        result = self.service.run(
            task_type=TaskType.DOMAIN_DETECTION,
            algorithm_id="const",
            data=self.demo_data,
            parameters={
                "n_clusters": 3,
                "epochs": 2,
                "neighbor_k": 3,
                "random_state": 23,
            },
        )

        self.assertEqual(RunStatus.SUCCEEDED, result.status)
        self.assertEqual("const", result.algorithm_id)
        self.assertEqual("conST", result.summary["backend"])
        self.assertEqual(3, result.summary["predicted_domains"])

        assignments = json.loads(
            Path(result.artifacts[0]["uri"]).read_text(encoding="utf-8")
        )
        self.assertEqual("const", assignments["algorithm_id"])
        self.assertEqual(
            self.demo_data.metadata["spot_count"],
            len(assignments["domains"]),
        )

    @unittest.skipUnless(PYG_AVAILABLE, "DeepST dependencies are not installed")
    def test_deepst_domain_detection_runs_real_backend(self) -> None:
        result = self.service.run(
            task_type=TaskType.DOMAIN_DETECTION,
            algorithm_id="deepst",
            data=self.demo_data,
            parameters={
                "n_clusters": 3,
                "pre_epochs": 1,
                "epochs": 1,
                "neighbor_k": 3,
                "random_state": 29,
            },
        )

        self.assertEqual(RunStatus.SUCCEEDED, result.status)
        self.assertEqual("deepst", result.algorithm_id)
        self.assertEqual("DeepST", result.summary["backend"])
        self.assertEqual(3, result.summary["predicted_domains"])

        assignments = json.loads(
            Path(result.artifacts[0]["uri"]).read_text(encoding="utf-8")
        )
        self.assertEqual("deepst", assignments["algorithm_id"])
        self.assertEqual(
            self.demo_data.metadata["spot_count"],
            len(assignments["domains"]),
        )


if __name__ == "__main__":
    unittest.main()

