from __future__ import annotations

from typing import Any, Iterable, Mapping

from st_platform.algorithms.base import Algorithm, AlgorithmOutput, AlgorithmSpec
from st_platform.algorithms.ccst import CCSTDomainAlgorithm
from st_platform.algorithms.const import ConSTDomainAlgorithm
from st_platform.algorithms.deepst import DeepSTDomainAlgorithm
from st_platform.algorithms.graphst import GraphSTDomainAlgorithm
from st_platform.algorithms.sedr import SEDRDomainAlgorithm
from st_platform.algorithms.spagcn import SpaGCNDomainAlgorithm
from st_platform.algorithms.spagcn_lite import SpaGCNLiteDomainAlgorithm
from st_platform.data import SpatialDataBundle
from st_platform.tasks import TaskType


class DemoQualityControlAlgorithm(Algorithm):
    spec = AlgorithmSpec(
        algorithm_id="demo-qc",
        name="Demo QC",
        task_type=TaskType.QUALITY_CONTROL,
        runtime="python",
        version="0.1.0",
        description="A placeholder QC algorithm used to validate the platform execution flow.",
        tags=("demo", "qc"),
    )

    def run(
        self,
        data: SpatialDataBundle,
        parameters: Mapping[str, Any],
        context: Mapping[str, Any],
    ) -> AlgorithmOutput:
        summary = {
            "message": "Demo QC completed.",
            "dataset": data.summary(),
            "applied_parameters": dict(parameters),
        }
        return AlgorithmOutput(
            summary=summary,
            artifacts=[
                {
                    "kind": "report",
                    "name": "qc-summary.json",
                    "uri": f"{context['run_root']}/qc-summary.json",
                    "description": "Placeholder QC report path for future serialization.",
                }
            ],
            metrics={
                "spot_count": 4281.0,
                "median_detected_genes": 2510.0,
            },
        )


class MockDomainDetectionAlgorithm(Algorithm):
    spec = AlgorithmSpec(
        algorithm_id="mock-domain",
        name="Mock Domain Detection",
        task_type=TaskType.DOMAIN_DETECTION,
        runtime="python",
        version="0.1.0",
        description="A placeholder spatial domain detector for validating registry and runner behavior.",
        tags=("demo", "domain"),
    )

    def run(
        self,
        data: SpatialDataBundle,
        parameters: Mapping[str, Any],
        context: Mapping[str, Any],
    ) -> AlgorithmOutput:
        resolution = parameters.get("resolution", 0.8)
        return AlgorithmOutput(
            summary={
                "message": "Mock domain detection completed.",
                "dataset": data.summary(),
                "predicted_domains": 6,
                "resolution": resolution,
            },
            artifacts=[
                {
                    "kind": "plot",
                    "name": "domain-map.html",
                    "uri": f"{context['run_root']}/domain-map.html",
                    "description": "Placeholder spatial domain map.",
                }
            ],
            metrics={
                "silhouette_score": 0.61,
                "moran_i_mean": 0.33,
            },
        )


class MockDeconvolutionAlgorithm(Algorithm):
    spec = AlgorithmSpec(
        algorithm_id="mock-deconv",
        name="Mock Deconvolution",
        task_type=TaskType.DECONVOLUTION,
        runtime="python",
        version="0.1.0",
        description="A placeholder deconvolution adapter that shows how future methods should integrate.",
        tags=("demo", "deconvolution"),
    )

    def run(
        self,
        data: SpatialDataBundle,
        parameters: Mapping[str, Any],
        context: Mapping[str, Any],
    ) -> AlgorithmOutput:
        return AlgorithmOutput(
            summary={
                "message": "Mock deconvolution completed.",
                "dataset": data.summary(),
                "estimated_cell_types": ["T_cell", "B_cell", "Myeloid"],
            },
            artifacts=[
                {
                    "kind": "table",
                    "name": "cell-type-fractions.csv",
                    "uri": f"{context['run_root']}/cell-type-fractions.csv",
                    "description": "Placeholder cell type fraction output.",
                }
            ],
            metrics={
                "mean_entropy": 0.45,
                "reference_overlap": 0.72,
            },
            warnings=[
                "Reference signatures are mocked in the scaffold version.",
            ],
        )


def build_builtin_algorithms() -> Iterable[Algorithm]:
    return [
        DemoQualityControlAlgorithm(),
        MockDomainDetectionAlgorithm(),
        CCSTDomainAlgorithm(),
        ConSTDomainAlgorithm(),
        DeepSTDomainAlgorithm(),
        GraphSTDomainAlgorithm(),
        SEDRDomainAlgorithm(),
        SpaGCNDomainAlgorithm(),
        SpaGCNLiteDomainAlgorithm(),
        MockDeconvolutionAlgorithm(),
    ]

