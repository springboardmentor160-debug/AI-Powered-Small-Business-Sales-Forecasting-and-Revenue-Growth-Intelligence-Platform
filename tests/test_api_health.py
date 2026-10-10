from fastapi.testclient import TestClient

from backend.main import app


def test_root_endpoint_returns_application_metadata():
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "application": "MarketMind AI",
        "version": "2.1.0",
        "status": "online",
    }


def test_health_endpoint_returns_healthy_status():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "MarketMind AI backend",
        "version": "2.1.0",
    }
