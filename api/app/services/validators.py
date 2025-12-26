# app/services/validators.py
import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


def validate_coordinates(latitude: float, longitude: float):
    """Checks if coordinates are within global limits."""
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        logger.warning(f"Coordenadas inválidas: {latitude}, {longitude}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coordenadas fora dos limites globais (Lat: -90 a 90, Lon: -180 a 180)."
        )


def validate_search_radius(radius_km: float):
    """Validates the search radius according to business limits."""
    if radius_km <= 0:
        logger.warning(f"Raio inválido: {radius_km}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O raio de busca deve ser um valor positivo."
        )
    if radius_km > 1000:
        logger.warning(f"Raio excessivo: {radius_km}km")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O raio de busca máximo permitido é de 1000km."
        )


def validate_imovel_id(id: str):
    """Checks if the ID is valid (not empty)."""
    if not id or not id.strip():
        logger.warning("Tentativa de acesso com ID vazio.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O ID da fazenda não pode estar vazio."
        )
