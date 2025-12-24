import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

# Importação absoluta (ajustada para o PYTHONPATH=api)
from app.main import app
from app.database import get_db


@pytest.fixture
def client():
    """Fixture que cria o cliente de teste sem depender de arquivos externos"""
    mock_db = MagicMock()

    def override_get_db():
        yield mock_db
    app.dependency_overrides[get_db] = override_get_db

    # Criamos o cliente usando a sintaxe mais segura para evitar o TypeError
    c = TestClient(app)
    yield c
    app.dependency_overrides.clear()


def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200


def test_health_check(client, monkeypatch):
    # We forced the database mock so the health check could pass.
    mock_execute = MagicMock()
    monkeypatch.setattr("sqlalchemy.orm.Session.execute", mock_execute)
    response = client.get("/health")
    assert response.status_code == 200


def test_pagination_invalid_values(client):
    # Pagination Test
    payload = {
        "latitude": -21.0, "longitude": -51.0,
        "radius_km": 10, "page": 0, "size": 3
    }
    response = client.post("/fazendas/busca-raio", json=payload)
    # Se retornar 422, o seu Pydantic (ge=1) está funcionando!
    assert response.status_code == 422
