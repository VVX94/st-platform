from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from st_platform.api.deps import get_platform_service
from st_platform.api.schemas import AlgorithmOut

router = APIRouter()


@router.get("/api/algorithms", response_model=List[AlgorithmOut])
async def list_algorithms() -> List[AlgorithmOut]:
    service = get_platform_service()
    specs = service.list_algorithms()
    return [
        AlgorithmOut(
            algorithm_id=s["algorithm_id"],
            name=s["name"],
            task_type=s["task_type"],
            runtime=s["runtime"],
            version=s["version"],
            description=s["description"],
            tags=s.get("tags", []),
        )
        for s in specs
    ]


@router.get("/api/algorithms/{algorithm_id}", response_model=AlgorithmOut)
async def get_algorithm(algorithm_id: str) -> AlgorithmOut:
    service = get_platform_service()
    specs = service.list_algorithms()
    for s in specs:
        if s["algorithm_id"] == algorithm_id:
            return AlgorithmOut(
                algorithm_id=s["algorithm_id"],
                name=s["name"],
                task_type=s["task_type"],
                runtime=s["runtime"],
                version=s["version"],
                description=s["description"],
                tags=s.get("tags", []),
            )
    raise HTTPException(status_code=404, detail=f"Algorithm '{algorithm_id}' not found")
