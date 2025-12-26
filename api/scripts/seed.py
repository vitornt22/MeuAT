import os
import logging
import time
import geopandas as gpd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.logging_config import setup_logging
from app.database import engine

# Initialize structured logging
setup_logging()
logger = logging.getLogger(__name__)

# Constants for file paths and limits
# Note: The 'data' folder is at the root, mapped to /app/data in Docker
DATA_DIR = os.getenv("DATA_PATH", "/app/data")
FILE_NAME = "AREA_IMOVEL_1.shp"
TABLE_NAME = "farms"
LIMIT_ROWS = 3000  # Limit for technical test performance


def wait_for_db(retries=10, interval=3):
    """Wait for the database to become available and healthy."""
    logger.info("Verificando conexão com o banco de dados...")
    for i in range(retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                return True
        except Exception:
            logger.warning(
                f"Banco de dados não está pronto... ({i+1}/{retries})")
            time.sleep(interval)
    return False


def is_db_populated():
    """Check if the table exists and already contains data."""
    try:
        with engine.connect() as conn:
            # Check if table 'farms' exists and has rows
            query = text(f"SELECT COUNT(*) FROM {TABLE_NAME}")
            result = conn.execute(query)
            count = result.scalar()
            return count > 0
    except Exception:
        # Table probably doesn't exist yet
        return False


def create_indexes():
    """Create Spatial (GIST) and B-Tree indexes for performance."""
    logger.info("Criando chaves primárias e índices espaciais...")
    with engine.connect() as conn:
        try:
            # Primary Key (Unique CAR ID)
            conn.execute(
                text(f"ALTER TABLE {TABLE_NAME} ADD PRIMARY KEY (imovel_code);"))
            # Spatial Index for Geo queries
            conn.execute(text(
                f"CREATE INDEX IF NOT EXISTS idx_geom ON {TABLE_NAME} USING GIST (geometry);"))
            # City index for text search
            conn.execute(
                text(f"CREATE INDEX IF NOT EXISTS idx_city ON {TABLE_NAME} (city);"))
            conn.commit()
            logger.info("Otimização: Índices criados com sucesso.")
        except SQLAlchemyError as e:
            logger.error(f"Falha ao criar índices: {e}")
            conn.rollback()


def run_seed():
    """Main execution flow for seeding the database."""
    if not wait_for_db():
        logger.error(
            "Não foi possível conectar ao banco de dados. Abortando seed.")
        return

    # REQUIREMENT: Only execute once
    if is_db_populated():
        logger.info(
            "O banco de dados já está populado. Pulando o processo de seed.")
        return

    # Support multiple extensions for flexibility (GeoJSON or Shapefile)
    file_path = os.path.join(DATA_DIR, FILE_NAME)

    if not os.path.exists(file_path):
        logger.error(f"Arquivo não encontrado em: {file_path}")
        return

    try:
        logger.info(f"Carregando dados de: {file_path}")
        # GeoPandas handles the .shp/.dbf/.shx cluster automatically
        df = gpd.read_file(file_path, rows=LIMIT_ROWS)

        if df.empty:
            logger.warning("O arquivo de entrada está vazio.")
            return

        # Transform to WGS84 (Standard for Web/Leaflet)
        df = df.to_crs(epsg=4326)

        # Map internal CAR names to our API Schema
        column_mapping = {
            'cod_imovel': 'imovel_code',
            'municipio': 'city',
            'cod_estado': 'state_code',
            'num_area': 'area_size',
            'mod_fiscal': 'fiscal_module',
            'ind_status': 'status',
            'ind_tipo': 'type',
            'dat_criaca': 'created_at',
            'geometry': 'geometry'
        }

        # Filter only available columns
        existing_cols = {k: v for k,
                         v in column_mapping.items() if k in df.columns}
        # Renaming columns to english
        df = df[list(existing_cols.keys())].rename(columns=existing_cols)
        # Removing duplicates
        df = df.drop_duplicates(subset=['imovel_code'])

        logger.info(f"Ingerindo {len(df)} registros no PostGIS...")
        # Write to database
        df.to_postgis(TABLE_NAME, engine, if_exists="replace", index=False)

        # Add indexes after ingestion for faster writes
        create_indexes()

        logger.info("Processo de seed finalizado com sucesso!")

    except Exception as e:
        logger.critical(
            f"Falha crítica durante o seed: {str(e)}", exc_info=True)


if __name__ == "__main__":
    run_seed()
