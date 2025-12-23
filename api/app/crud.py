from sqlalchemy.orm import Session
from geoalchemy2.functions import ST_Contains, ST_DWithin, ST_SetSRID, ST_Point, ST_AsText
from .models.farm import Farm


def get_base_query(db: Session):
    return db.query(
        Farm.imovel_code, Farm.city, Farm.state_code,
        Farm.area_size, Farm.fiscal_module, Farm.status,
        Farm.type, Farm.created_at,
        ST_AsText(Farm.geom).label("geometry")
    )


def get_by_id(db: Session, farm_id: str):
    return get_base_query(db).filter(Farm.imovel_code == farm_id).first()


def search_by_point(db: Session, lat: float, lon: float):
    pt = ST_SetSRID(ST_Point(lon, lat), 4326)
    return get_base_query(db).filter(ST_Contains(Farm.geom, pt)).all()


def search_by_radius(db: Session, lat: float, lon: float, km: float):
    pt = ST_SetSRID(ST_Point(lon, lat), 4326)
    return get_base_query(db).filter(ST_DWithin(Farm.geom, pt, km * 1000, True)).all()
