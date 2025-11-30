"""Tests for task failure handling"""

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import flow_engine, task_registry
from app.models import FlowDefinition
from app.services.tasks import task_always_fails


def test_task1_failure_stops_flow(client: TestClient):
    """Test that task1 failure stops the flow"""
    # Register a flow with failure scenario
    flow_def = {
        "flow": {
            "id": "test_failure_flow",
            "name": "Failure Test Flow",
            "start_task": "task1",
            "tasks": [
                {"name": "task1", "description": "Fetch data"},
                {"name": "task2", "description": "Process data"},
                {"name": "task3", "description": "Store data"},
            ],
            "conditions": [
                {
                    "name": "condition_task1",
                    "description": "Check task1",
                    "source_task": "task1",
                    "outcome": "success",
                    "target_task_success": "task2",
                    "target_task_failure": "end",  # Should go to end on failure
                },
                {
                    "name": "condition_task2",
                    "description": "Check task2",
                    "source_task": "task2",
                    "outcome": "success",
                    "target_task_success": "task3",
                    "target_task_failure": "end",
                },
            ],
        }
    }

    # Register flow
    client.post("/api/v1/flows/register", json=flow_def)

    # Create a custom task that fails
    def failing_task1(context):
        from app.models import TaskResult, TaskStatus

        return TaskResult(
            status=TaskStatus.FAILURE, message="Task1 intentionally failed"
        )

    # Override task1 temporarily
    original_task1 = task_registry.get("task1")
    task_registry.register("task1", failing_task1)

    try:
        # Execute flow
        response = client.post("/api/v1/flows/test_failure_flow/execute")
        assert response.status_code == 200

        data = response.json()
        status = data["status"]

        # Verify only task1 was executed
        assert len(status["completed_tasks"]) == 1
        assert "task1" in status["completed_tasks"]
        assert "task2" not in status["completed_tasks"]
        assert "task3" not in status["completed_tasks"]

        # Verify task1 failed
        assert status["task_results"]["task1"]["status"] == "failure"

        # Verify flow completed (but with failure)
        assert status["status"] in ["completed", "completed_with_failures"]

    finally:
        # Restore original task
        task_registry.register("task1", original_task1)


def test_task2_failure_stops_flow(client: TestClient):
    """Test that task2 failure prevents task3 execution"""
    flow_def = {
        "flow": {
            "id": "test_task2_failure",
            "name": "Task2 Failure Test",
            "start_task": "task1",
            "tasks": [
                {"name": "task1", "description": "Fetch data"},
                {"name": "task2", "description": "Process data"},
                {"name": "task3", "description": "Store data"},
            ],
            "conditions": [
                {
                    "name": "condition_task1",
                    "description": "Check task1",
                    "source_task": "task1",
                    "outcome": "success",
                    "target_task_success": "task2",
                    "target_task_failure": "end",
                },
                {
                    "name": "condition_task2",
                    "description": "Check task2",
                    "source_task": "task2",
                    "outcome": "success",
                    "target_task_success": "task3",
                    "target_task_failure": "end",  # Should stop here
                },
            ],
        }
    }

    client.post("/api/v1/flows/register", json=flow_def)

    # Override task2 to fail
    def failing_task2(context):
        from app.models import TaskResult, TaskStatus

        return TaskResult(
            status=TaskStatus.FAILURE, message="Task2 intentionally failed"
        )

    original_task2 = task_registry.get("task2")
    task_registry.register("task2", failing_task2)

    try:
        response = client.post("/api/v1/flows/test_task2_failure/execute")
        assert response.status_code == 200

        status = response.json()["status"]

        # Task1 should succeed, task2 should fail, task3 should not run
        assert len(status["completed_tasks"]) == 2
        assert "task1" in status["completed_tasks"]
        assert "task2" in status["completed_tasks"]
        assert "task3" not in status["completed_tasks"]

        assert status["task_results"]["task1"]["status"] == "success"
        assert status["task_results"]["task2"]["status"] == "failure"

    finally:
        task_registry.register("task2", original_task2)


def test_all_tasks_succeed(client: TestClient):
    """Test that all tasks execute when no failures occur"""
    response = client.post("/api/v1/flows/flow123/execute")
    assert response.status_code == 200

    status = response.json()["status"]

    # All tasks should complete
    assert len(status["completed_tasks"]) == 3
    assert "task1" in status["completed_tasks"]
    assert "task2" in status["completed_tasks"]
    assert "task3" in status["completed_tasks"]

    # All should succeed
    assert status["task_results"]["task1"]["status"] == "success"
    assert status["task_results"]["task2"]["status"] == "success"
    assert status["task_results"]["task3"]["status"] == "success"

    assert status["status"] == "completed"


def test_failure_message_included(client: TestClient):
    """Test that failure messages are properly captured"""
    flow_def = {
        "flow": {
            "id": "test_failure_message",
            "name": "Failure Message Test",
            "start_task": "task1",
            "tasks": [{"name": "task1", "description": "Task"}],
            "conditions": [
                {
                    "name": "condition_task1",
                    "description": "Check task1",
                    "source_task": "task1",
                    "outcome": "success",
                    "target_task_success": "end",
                    "target_task_failure": "end",
                }
            ],
        }
    }

    client.post("/api/v1/flows/register", json=flow_def)

    def failing_task_with_message(context):
        from app.models import TaskResult, TaskStatus

        return TaskResult(
            status=TaskStatus.FAILURE,
            message="Specific error: Database connection failed",
        )

    original_task1 = task_registry.get("task1")
    task_registry.register("task1", failing_task_with_message)

    try:
        response = client.post("/api/v1/flows/test_failure_message/execute")
        assert response.status_code == 200

        status = response.json()["status"]
        task_result = status["task_results"]["task1"]

        assert task_result["status"] == "failure"
        assert "Database connection failed" in task_result["message"]

    finally:
        task_registry.register("task1", original_task1)


def test_execution_status_reflects_failure(client: TestClient):
    """Test that execution status properly reflects failures"""
    flow_def = {
        "flow": {
            "id": "test_status_failure",
            "name": "Status Failure Test",
            "start_task": "task1",
            "tasks": [{"name": "task1", "description": "Task"}],
            "conditions": [
                {
                    "name": "condition_task1",
                    "description": "Check task1",
                    "source_task": "task1",
                    "outcome": "success",
                    "target_task_success": "end",
                    "target_task_failure": "end",
                }
            ],
        }
    }

    client.post("/api/v1/flows/register", json=flow_def)

    # Task that fails
    def failing_task(context):
        from app.models import TaskResult, TaskStatus

        return TaskResult(status=TaskStatus.FAILURE, message="Failed")

    original_task1 = task_registry.get("task1")
    task_registry.register("task1", failing_task)

    try:
        exec_response = client.post("/api/v1/flows/test_status_failure/execute")
        execution_id = exec_response.json()["execution_id"]

        # Check execution status
        status_response = client.get(f"/api/v1/flows/execution/{execution_id}")
        status = status_response.json()

        # Status should indicate completion with failures
        assert status["status"] in ["completed", "completed_with_failures"]
        assert (
            "failure" in status["message"].lower()
            or "failed" in status["message"].lower()
        )

    finally:
        task_registry.register("task1", original_task1)
