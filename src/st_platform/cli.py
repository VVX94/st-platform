from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Optional

from st_platform.tasks import TaskType
from st_platform.workflows import create_platform_service


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="st-platform",
        description="Phase-1 scaffold CLI for the spatial transcriptomics platform.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-tasks", help="List default platform tasks.")

    list_algorithms = subparsers.add_parser("list-algorithms", help="List registered algorithms.")
    list_algorithms.add_argument(
        "--task",
        choices=[task.value for task in TaskType],
        help="Optional task filter.",
    )

    run_demo = subparsers.add_parser("run-demo", help="Run a demo task with the built-in sample dataset.")
    run_demo.add_argument(
        "--task",
        choices=[task.value for task in TaskType],
        required=True,
        help="Task type to execute.",
    )
    run_demo.add_argument(
        "--algorithm",
        required=True,
        help="Algorithm id to execute.",
    )
    run_demo.add_argument(
        "--project-root",
        default=str(Path.cwd()),
        help="Project root used to create the runs directory.",
    )

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    project_root = getattr(args, "project_root", str(Path.cwd()))
    service = create_platform_service(project_root=project_root)

    if args.command == "list-tasks":
        _print_json(service.list_tasks())
        return 0

    if args.command == "list-algorithms":
        task = TaskType(args.task) if args.task else None
        _print_json(service.list_algorithms(task))
        return 0

    if args.command == "run-demo":
        task_type = TaskType(args.task)
        demo_data = service.build_demo_dataset()
        parameters = _default_parameters_for_demo(
            task_type=task_type,
            algorithm_id=args.algorithm,
        )
        result = service.run(
            task_type=task_type,
            algorithm_id=args.algorithm,
            data=demo_data,
            parameters=parameters,
        )
        _print_json(result.to_dict())
        return 0 if result.status.value == "succeeded" else 1

    parser.error(f"Unsupported command: {args.command}")
    return 2


def _default_parameters_for_demo(task_type: TaskType, algorithm_id: str) -> Dict[str, Any]:
    algorithm_defaults = {
        "spagcn": {
            "n_clusters": 3,
            "neighbor_k": 3,
            "num_pcs": 2,
            "l": 1.0,
            "max_epochs": 2,
            "random_state": 0,
        },
        "spagcn-lite": {
            "n_clusters": 3,
            "neighbor_k": 3,
            "spatial_weight": 0.25,
            "random_state": 0,
        },
    }
    return algorithm_defaults.get(algorithm_id, _default_parameters_for_task(task_type))


def _default_parameters_for_task(task_type: TaskType) -> Dict[str, Any]:
    defaults = {
        TaskType.QUALITY_CONTROL: {"min_features": 200, "max_mito_ratio": 0.2},
        TaskType.DOMAIN_DETECTION: {"resolution": 0.8},
        TaskType.DECONVOLUTION: {"normalize": True},
        TaskType.CROSS_MODAL_MAPPING: {"top_k": 20},
    }
    return defaults.get(task_type, {})


def _print_json(payload: Any) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))

