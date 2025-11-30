"""Flow registration tests"""

import pytest
from fastapi.testclient import TestClient


def test_register_flow_success(client: TestClient, sample_flow_definition):
    """Test successful flow registration"""
    response = client.post("/api/v1/flows/register", json=sample_flow_definition)

    assert response.status_code == 201
    data = response.json()

    assert data["message"] == "Flow registered successfully"
    assert data["flow_id"] == "test_flow_001"
    assert data["flow_name"] == "Test Flow"


def test_register_flow_appears_in_list(client: TestClient, sample_flow_definition):
    """Test that registered flow appears in flow list"""
    # Register flow
    client.post("/api/v1/flows/register", json=sample_flow_definition)

    # List flows
    response = client.get("/api/v1/flows")
    data = response.json()

    flow_ids = [flow["id"] for flow in data["flows"]]
    assert "test_flow_001" in flow_ids


def test_register_invalid_flow(client: TestClient, invalid_flow_definition):
    """Test registering invalid flow returns error"""
    response = client.post("/api/v1/flows/register", json=invalid_flow_definition)

    assert response.status_code == 400
    assert "detail" in response.json()


def test_register_flow_missing_fields(client: TestClient):
    """Test registering flow with missing required fields"""
    incomplete_flow = {
        "flow": {
            "id": "incomplete",
            "name": "Incomplete Flow"
            # Missing start_task, tasks, conditions
        }
    }

    response = client.post("/api/v1/flows/register", json=incomplete_flow)

    assert response.status_code == 422  # Validation error


def test_register_flow_invalid_json(client: TestClient):
    """Test registering flow with invalid JSON structure"""
    response = client.post("/api/v1/flows/register", json={"invalid": "structure"})

    assert response.status_code == 422
