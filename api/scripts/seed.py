import os
import geopandas as gpd
from sqlalchemy import create_engine, text
# Agora o import funciona direto porque /app está no PYTHONPATH
from app.database import engine


def run_seed():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found.")
        return

    # Usamos o engine que já configuramos no app/database.py
    # para manter uma única fonte de verdade
    shapefile_path = "data/AREA_IMOVEL_1.shp"

    if not os.path.exists(shapefile_path):
        print(f"File not found: {shapefile_path}")
        return

    print("--- Loading Data ---")
    df = gpd.read_file(shapefile_path, rows=500)
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
        'geometry': 'geom'
    }

    df = df[list(column_mapping.keys())].rename(columns=column_mapping)

    print("Writing to PostGIS...")
    df.to_postgis("farms", engine, if_exists="replace", index=False)

    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE farms ADD PRIMARY KEY (imovel_code);"))
        conn.execute(
            text("CREATE INDEX IF NOT EXISTS idx_farms_geom ON farms USING GIST (geom);"))
        conn.commit()

    print("Seed finished!")


if __name__ == "__main__":
    run_seed()
