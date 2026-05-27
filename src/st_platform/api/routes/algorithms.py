from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from st_platform.api.deps import get_platform_service
from st_platform.api.schemas import AlgorithmOut

router = APIRouter()


@router.get("/api/algorithms", response_model=List[AlgorithmOut])
async def list_algorithms() -> List[AlgorithmOut]:
    service = get_platform_service()
    results = []
    for algo in service.algorithm_registry.list():
        s = algo.spec.to_dict()
        results.append(
            AlgorithmOut(
                algorithm_id=s["algorithm_id"],
                name=s["name"],
                task_type=s["task_type"],
                runtime=s["runtime"],
                version=s["version"],
                description=s["description"],
                tags=s.get("tags", []),
                available=algo.is_available(),
            )
        )
    return results


@router.get("/api/algorithms/{algorithm_id}", response_model=AlgorithmOut)
async def get_algorithm(algorithm_id: str) -> AlgorithmOut:
    service = get_platform_service()
    try:
        algo = service.algorithm_registry.get(algorithm_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Algorithm '{algorithm_id}' not found")
    s = algo.spec.to_dict()
    return AlgorithmOut(
        algorithm_id=s["algorithm_id"],
        name=s["name"],
        task_type=s["task_type"],
        runtime=s["runtime"],
        version=s["version"],
        description=s["description"],
        tags=s.get("tags", []),
        available=algo.is_available(),
    )
