from fastapi import FastAPI
from app.constants import descriptions
import logging
from fastapi.middleware.cors import CORSMiddleware

from app.routers import farms, infra
from app.logging_config import setup_logging

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, use apenas o endereço do seu front
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Including Routers
app.include_router(farms.router)
app.include_router(infra.router)
