import os
import logging
import time
import geopandas as gpd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from app.logging_config import setup_logging
from app.database import engine  # Ele usará a engine configurada no app

# Logs Settings
setup_logging()
logger = logging.getLogger(__name__)


def wait_for_db(retries=10, interval=3):
    """It waits the database to be ready"""
    for i in range(retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                return True
        except Exception:
            logger.warning(f"Aguardando banco de dados... ({i+1}/{retries})")
            time.sleep(interval)
    return False


def create_indexes_and_constraints():
    """Otimization: Primary Keys and Spacial Indexes"""
    logger.info("--- Iniciando Otimização: PK e Índices ---")
    with engine.connect() as conn:
        try:
            # Primary Key
            conn.execute(
                text("ALTER TABLE farms ADD PRIMARY KEY (imovel_code);"))
            # Spacial Index(GiST)
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_farms_geom ON farms USING GIST (geometry);"))
            # Text Index
            conn.execute(
                text("CREATE INDEX IF NOT EXISTS idx_farms_city ON farms (city);"))
            conn.commit()
            logger.info("PK e Índices criados com sucesso!")
        except SQLAlchemyError as e:
            logger.error(f"Erro ao criar índices: {e}")
            conn.rollback()


def run_seed():
    # Fallback to local execution if enviromment don't have a variable
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.warning("DATABASE_URL não encontrada. Usando padrão local.")
        # If it executes locally, it will try the localhost
        os.environ["DATABASE_URL"] = "postgresql://admin:password@localhost:5432/meuat_geo"

    if not wait_for_db():
        logger.error("Falha ao conectar no banco de dados. Abortando.")
        return

    # Egde Case: verify possible paths
    possible_paths = ["data/AREA_IMOVEL_1.shp",
                      "/app/data/AREA_IMOVEL_1.shp", "../data/AREA_IMOVEL_1.shp"]
    shapefile_path = next(
        (p for p in possible_paths if os.path.exists(p)), None)

    if not shapefile_path:
        logger.error(
            "Shapefile não encontrado em nenhum dos caminhos esperados.")
        return

    try:
        logger.info(f"--- Lendo Shapefile de: {shapefile_path} ---")
        df = gpd.read_file(shapefile_path, rows=3000)

        if df.empty:
            logger.warning("O arquivo Shapefile está vazio.")
            return

        df = df.to_crs(epsg=4326)

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

        # It filters only what exists in the file to avoid KeyError
        existing_cols = {k: v for k,
                         v in column_mapping.items() if k in df.columns}
        df = df[list(existing_cols.keys())].rename(columns=existing_cols)

        df = df.drop_duplicates(subset=['imovel_code'])

        logger.info(f"Gravando {len(df)} registros no PostGIS...")
        # if_exists="replace" recreates the table. index=False avoid extra ID column
        df.to_postgis("farms", engine, if_exists="replace", index=False)

        create_indexes_and_constraints()
        logger.info("Seed finalizado com sucesso!")

    except Exception as e:
        logger.critical(f"Falha no Seed: {str(e)}")


if __name__ == "__main__":
    run_seed()
