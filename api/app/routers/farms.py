from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import crud
from ..schemas.farm import FarmResponse, PointSearch, RadiusSearch

router = APIRouter(prefix="/farms", tags=["Farms"])


@router.get("/{id}", response_model=FarmResponse)
def read_farm(id: str, db: Session = Depends(get_db)):
    db_farm = crud.get_by_id(db, id)
    if not db_farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return db_farm


@router.post("/search-point", response_model=List[FarmResponse])
def search_point(payload: PointSearch, db: Session = Depends(get_db)):
    return crud.search_by_point(db, payload.latitude, payload.longitude)


@router.post("/search-radius", response_model=List[FarmResponse])
def search_radius(payload: RadiusSearch, db: Session = Depends(get_db)):
    return crud.search_by_radius(
        db,
        payload.latitude,
        payload.longitude,
        payload.radius_km
    )
