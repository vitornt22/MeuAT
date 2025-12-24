import json
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from geoalchemy2.functions import ST_Contains, ST_DWithin, ST_SetSRID, ST_Point, ST_AsGeoJSON
from .models.farm import Farm
from .schemas.farm import PointSearch, RadiusSearch, FilterParams

logger = logging.getLogger(__name__)


def apply_pagination(query, filters: FilterParams):
    """It Calculates the displacement (offset) and limits the results"""
    offset = (filters.page - 1) * filters.size
    return query.offset(offset).limit(filters.size)


def get_base_query(db: Session):
    return db.query(
        Farm.imovel_code, Farm.city, Farm.state_code,
        Farm.area_size, Farm.fiscal_module, Farm.status,
        Farm.type, Farm.created_at,
        ST_AsGeoJSON(Farm.geometry).label("geometry")
    )


def apply_extra_filters(query, filters: FilterParams):
    """
    Handling Edge Case: Empty Filters or Spaces within Strings
    """
    if filters.city and filters.city.strip():
        query = query.filter(Farm.city.ilike(f"%{filters.city.strip()}%"))

    if filters.area_min is not None:
        query = query.filter(Farm.area_size >= filters.area_min)

    if filters.area_max is not None:
        query = query.filter(Farm.area_size <= filters.area_max)

    return query


def format_records(results):
    """
    Handling an Edge Case: JSON Parsing Error.
    """
    output = []
    for r in results:
        try:
            item = dict(r._asdict())
            if item.get("geometry"):
                item["geometry"] = json.loads(item["geometry"])
            output.append(item)
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(
                f"Erro ao decodificar geometria do imóvel {r.imovel_code}: {e}")
            continue  # Pula o registro corrompido mas não derruba a API
    return output


def get_by_id(db: Session, farm_id: str):
    try:
        result = get_base_query(db).filter(Farm.imovel_code == farm_id).first()
        if result:
            return format_records([result])[0]
        return None
    except SQLAlchemyError as e:
        logger.error(f"Erro no banco ao buscar ID {farm_id}: {e}")
        raise HTTPException(
            status_code=500, detail="Erro interno na consulta ao banco de dados.")


def search_by_point(db: Session, payload: PointSearch):
    """
    It searchs farms cointaing the location specified with support for pagination filters
    """
    try:
        pt = ST_SetSRID(ST_Point(payload.longitude, payload.latitude), 4326)
        query = get_base_query(db).filter(ST_Contains(Farm.geometry, pt))

        # Applying extra filters
        query = apply_extra_filters(query, payload)

        # Applying pagination before executing the query
        query = apply_pagination(query, payload)

        return format_records(query.all())
    except SQLAlchemyError as e:
        logger.error(f"Erro espacial (Point): {e}")
        raise HTTPException(
            status_code=500, detail="Falha ao processar consulta geoespacial.")


def search_by_radius(db: Session, payload: RadiusSearch):
    """
    Busca fazendas em um raio informado com suporte a filtros e PAGINAÇÃO.
    """
    # Proteção de performance: evita raios negativos
    if payload.radius_km < 0:
        return []

    try:
        pt = ST_SetSRID(ST_Point(payload.longitude, payload.latitude), 4326)
        query = get_base_query(db).filter(
            ST_DWithin(Farm.geometry, pt, payload.radius_km * 1000, True)
        )

        # Applying extra filters
        query = apply_extra_filters(query, payload)

        # Applying pagination before executing the query
        query = apply_pagination(query, payload)

        return format_records(query.all())
    except SQLAlchemyError as e:
        logger.error(f"Erro espacial (Radius): {e}")
        raise HTTPException(
            status_code=500, detail="Falha ao processar consulta por raio.")
