from fastapi import FastAPI
from app.constants import descriptions
import logging

from app.routers import farms, infra
from app.logging_config import setup_logging
from app.database import get_db

# Setting Structured Logger
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="🛰️ Fazendas SP - API Geoespacial",
    description=descriptions.INITIAL_DESCRIPTION,
    version="1.0.0",
    contact={
        "name": "Seu Nome",
        "url": "https://seu-portfolio.com",
    }
)

# Including Routers
app.include_router(farms.router)
app.include_router(infra.router)
