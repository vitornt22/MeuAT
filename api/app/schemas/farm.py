from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Any

# GeoJSON Structure for Swagger documentation


# WKT - Well-Know Text - Textual Format
class GeoJSONModel(BaseModel):
    type: str  # e.g., "Polygon" or "Point"
    coordinates: List[Any]


class FilterParams(BaseModel):
    city: Optional[str] = None
    area_min: Optional[float] = None
    area_max: Optional[float] = None
    # Adding pagination with standart values
    page: int = Field(1, ge=1, description="Número da página")
    size: int = Field(5, ge=1, le=100, description="Registros por página")


class PointSearch(FilterParams):
    latitude: float
    longitude: float


class RadiusSearch(PointSearch):
    radius_km: float = Field(..., alias="raio_km")
    # It allows pydantic recognize both inner name and the alias
    model_config = ConfigDict(populate_by_name=True)


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
    geometry: GeoJSONModel
