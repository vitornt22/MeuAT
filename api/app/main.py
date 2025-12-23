from fastapi import FastAPI
from .routers import farms

app = FastAPI(title="MeuAT Geo-Spatial API")

app.include_router(farms.router)


@app.get("/health")
def health():
    return {"status": "up and running"}
