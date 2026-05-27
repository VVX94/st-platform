from __future__ import annotations

import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from st_platform.api.deps import get_db_session
from st_platform.api.schemas import DatasetCreate, DatasetOut
from st_platform.storage.models import DatasetModel
from st_platform.storage.repositories import DatasetRepo

router = APIRouter()


def _model_to_out(ds: DatasetModel) -> DatasetOut:
    try:
        meta = json.loads(ds.metadata_json)
    except (json.JSONDecodeError, TypeError):
        meta = {}
    return DatasetOut(
        dataset_id=ds.dataset_id,
        name=ds.name,
        platform=ds.platform,
        sample_id=ds.sample_id,
        uri=ds.uri,
        description=ds.description,
        metadata=meta,
        created_at=ds.created_at,
    )


@router.get("/api/datasets", response_model=List[DatasetOut])
async def list_datasets(db: Session = Depends(get_db_session)) -> List[DatasetOut]:
    repo = DatasetRepo(db)
    return [_model_to_out(ds) for ds in repo.list_all()]


@router.post("/api/datasets/register", response_model=DatasetOut, status_code=201)
async def register_dataset(
    payload: DatasetCreate,
    db: Session = Depends(get_db_session),
) -> DatasetOut:
    repo = DatasetRepo(db)
    ds = repo.create(
        name=payload.name,
        platform=payload.platform,
        sample_id=payload.sample_id,
        uri=payload.uri,
        description=payload.description,
        metadata=payload.metadata,
    )
    return _model_to_out(ds)


@router.get("/api/datasets/{dataset_id}", response_model=DatasetOut)
async def get_dataset(
    dataset_id: str,
    db: Session = Depends(get_db_session),
) -> DatasetOut:
    repo = DatasetRepo(db)
    ds = repo.get(dataset_id)
    if ds is None:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found")
    return _model_to_out(ds)
