"""Health endpoint tests"""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint returns 200"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_check_structure(client: TestClient):
    """Test health check response structure"""
    response = client.get("/health")
    data = response.json()

    assert "status" in data
    assert isinstance(data["status"], str)
