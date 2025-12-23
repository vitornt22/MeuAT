from pydantic import BaseModel, ConfigDict
from typing import Optional, List


class FarmResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    imovel_code: str
    city: Optional[str]
    state_code: Optional[str]
    area_size: Optional[float]
    fiscal_module: Optional[float]
    status: Optional[str]
    type: Optional[str]
    created_at: Optional[str]
    geometry: str


class PointSearch(BaseModel):
    latitude: float
    longitude: float


class RadiusSearch(PointSearch):
    radius_km: float
