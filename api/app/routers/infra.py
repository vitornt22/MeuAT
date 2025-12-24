
import logging
from app.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException, status

logger = logging.getLogger(__name__)
router = APIRouter(prefix="", tags=["Infra"])

# Infrastructure Endpoints  (Health e Root)


@router.get("/", tags=["Infra"])
async def root():
    return {"message": "API Geospacial ativa. Acesse /docs para documentação."}


@router.get("/health", tags=["Infra"])
def health_check(db: Session = Depends(get_db)):
    """
    Verify is API is online and if there is a functional database connection
    """
    try:
        # It execute a ultra soft query (SELECT 1) to test the database handshake
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        logger.critical(
            f"Health check falhou: Conexão com o banco perdida. Erro: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço indisponível: falha na conexão com o banco de dados"
        )
