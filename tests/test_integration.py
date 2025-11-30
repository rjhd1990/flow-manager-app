"""Integration tests"""

import pytest
from fastapi.testclient import TestClient


def test_full_workflow(client: TestClient, sample_flow_definition):
    """Test complete workflow: register, execute, check status"""

    # 1. Register flow
    register_response = client.post(
        "/api/v1/flows/register", json=sample_flow_definition
    )
    assert register_response.status_code == 201

    # 2. Verify flow is listed
    list_response = client.get("/api/v1/flows")
    flow_ids = [f["id"] for f in list_response.json()["flows"]]
    assert "test_flow_001" in flow_ids

    # 3. Execute flow
    exec_response = client.post("/api/v1/flows/test_flow_001/execute")
    assert exec_response.status_code == 200
    execution_id = exec_response.json()["execution_id"]

    # 4. Check execution status
    status_response = client.get(f"/api/v1/flows/execution/{execution_id}")
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "completed"


def test_multiple_executions(client: TestClient):
    """Test multiple executions of the same flow"""
    executions = []

    for _ in range(3):
        response = client.post("/api/v1/flows/flow123/execute")
        assert response.status_code == 200
        executions.append(response.json()["execution_id"])

    # All execution IDs should be unique
    assert len(set(executions)) == 3

    # All executions should be retrievable
    for exec_id in executions:
        response = client.get(f"/api/v1/flows/execution/{exec_id}")
        assert response.status_code == 200


def test_api_documentation_accessible(client: TestClient):
    """Test that API documentation endpoints are accessible"""
    # OpenAPI JSON
    response = client.get("/openapi.json")
    assert response.status_code == 200

    # Swagger UI (redirects)
    response = client.get("/docs", follow_redirects=False)
    assert response.status_code in [200, 307]
