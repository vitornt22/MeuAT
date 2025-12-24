from fastapi import APIRouter, Depends, HTTPException, status
from app.constants import descriptions, responses
from sqlalchemy.orm import Session
from typing import List
import logging
from ..database import get_db
from .. import crud
from ..schemas.farm import FarmResponse, PointSearch, RadiusSearch

# The logger uses the StructuredFormatter defined in setup_logging
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/fazendas", tags=["Fazendas"])


@router.get(
    "/{id}", response_model=FarmResponse, summary="Obter fazenda por ID (CAR)",
    description=descriptions.DESC_GET_BY_ID, responses=responses.FARM_BY_ID
)
def get_farm_by_id(id: str, db: Session = Depends(get_db)):
    """
    It returns a specific farm by ID (CAR)
    """
    if not id.strip():
        logger.warning("Tentativa de acesso com ID vazio.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O ID da fazenda não pode estar vazio."
        )

    logger.info(f"Busca por ID iniciada: {id}")

    try:
        db_farm = crud.get_by_id(db, id)
        if not db_farm:
            logger.info(f"Fazenda não encontrada: {id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fazenda com ID {id} não encontrada."
            )

        logger.info(f"Fazenda recuperada com sucesso: {id}")
        return db_farm
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Falha crítica na busca por ID {id}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar a requisição."
        )


@router.post(
    "/busca-ponto",
    response_model=List[FarmResponse],
    description=descriptions.DESC_BUSCA_PONTO,
    responses=responses.FARMS_BY_POINTS
)
def get_by_point(payload: PointSearch, db: Session = Depends(get_db)):
    """
    It searchs farm(s) containg the specified location with  support fo pagination
    """
    # Structured Log including pagination to audit performance
    logger.info(
        f"Requisição busca-ponto: Lat={payload.latitude}, Lon={payload.longitude}, "
        f"Pagina={payload.page}, Tamanho={payload.size}"
    )

    if not (-90 <= payload.latitude <= 90) or not (-180 <= payload.longitude <= 180):
        logger.warning(
            f"Coordenadas inválidas: {payload.latitude}, {payload.longitude}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coordenadas fora dos limites globais (Lat: -90 a 90, Lon: -180 a 180)."
        )

    try:
        results = crud.search_by_point(db, payload)
        logger.info(
            f"Busca-ponto finalizada. Resultados na página: {len(results)}")
        return results
    except Exception as e:
        logger.error("Erro inesperado no endpoint busca-ponto", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Erro interno no servidor.")


@router.post(
    "/busca-raio",
    response_model=List[FarmResponse],
    description=descriptions.DESC_BUSCA_RAIO,
    responses=responses.FARMS_BY_RADIUS
)
def get_by_radius(payload: RadiusSearch, db: Session = Depends(get_db)):
    """
    It Returns farms inside a radius (km) with support for pagination
    """
    logger.info(
        f"Requisição busca-raio: Lat={payload.latitude}, Lon={payload.longitude}, "
        f"Raio={payload.radius_km}km, Pagina={payload.page}, Tamanho={payload.size}"
    )

    # Business rules validations
    if payload.radius_km <= 0:
        logger.warning(f"Raio inválido: {payload.radius_km}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O raio de busca deve ser um valor positivo."
        )

    if payload.radius_km > 500:
        logger.warning(f"Raio excessivo: {payload.radius_km}km")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O raio de busca máximo permitido é de 500km."
        )

    if not (-90 <= payload.latitude <= 90) or not (-180 <= payload.longitude <= 180):
        logger.warning(
            f"Coordenadas inválidas para busca-raio: {payload.latitude}, {payload.longitude}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coordenadas geográficas inválidas."
        )

    try:
        results = crud.search_by_radius(db, payload)
        logger.info(
            f"Busca-raio finalizada. Resultados na página: {len(results)}")
        return results
    except Exception as e:
        logger.error("Erro inesperado no endpoint busca-raio", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Erro interno no servidor.")
