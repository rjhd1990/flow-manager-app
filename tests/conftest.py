"""Pytest configuration and fixtures - COMPLETE WORKING VERSION"""

import logging
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import flow_engine, task_registry
from app.main import app
from app.models import FlowDefinition

logger = logging.getLogger(__name__)


# Load default flow once for all tests
@pytest.fixture(scope="session", autouse=True)
def load_default_flow():
    """Load the default flow before any tests run"""
    sample_flow = {
        "flow": {
            "id": "flow123",
            "name": "Data processing flow",
            "start_task": "task1",
            "tasks": [
                {"name": "task1", "description": "Fetch data"},
                {"name": "task2", "description": "Process data"},
                {"name": "task3", "description": "Store data"},
            ],
            "conditions": [
                {
                    "name": "condition_task1_result",
                    "description": "Evaluate the result of task1",
                    "source_task": "task1",
                    "outcome": "success",
                    "target_task_success": "task2",
                    "target_task_failure": "end",
                },
                {
                    "name": "condition_task2_result",
                    "description": "Evaluate the result of task2",
                    "source_task": "task2",
                    "outcome": "success",
                    "target_task_success": "task3",
                    "target_task_failure": "end",
                },
            ],
        }
    }

    # Register the flow if not already registered
    if "flow123" not in flow_engine.flow_definitions:
        flow_def = FlowDefinition(**sample_flow)
        flow_engine.register_flow(flow_def)
        logger.info("\n✓ Loaded default flow: flow123")

    yield

    # Cleanup after all tests complete
    flow_engine.flow_definitions.clear()
    flow_engine.executions.clear()


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def sample_flow_definition():
    """Sample flow definition for testing"""
    return {
        "flow": {
            "id": "test_flow_001",
            "name": "Test Flow",
            "start_task": "task1",
            "tasks": [
                {"name": "task1", "description": "Fetch data"},
                {"name": "task2", "description": "Process data"},
                {"name": "task3", "description": "Store data"},
            ],
            "conditions": [
                {
                    "name": "condition_task1",
                    "description": "Evaluate task1",
                    "source_task": "task1",
                    "outcome": "success",
                    "target_task_success": "task2",
                    "target_task_failure": "end",
                },
                {
                    "name": "condition_task2",
                    "description": "Evaluate task2",
                    "source_task": "task2",
                    "outcome": "success",
                    "target_task_success": "task3",
                    "target_task_failure": "end",
                },
            ],
        }
    }


@pytest.fixture
def invalid_flow_definition():
    """Invalid flow definition for testing error handling"""
    return {
        "flow": {
            "id": "invalid_flow",
            "name": "Invalid Flow",
            "start_task": "nonexistent_task",
            "tasks": [{"name": "task1", "description": "Task 1"}],
            "conditions": [],
        }
    }


@pytest.fixture(autouse=True)
def reset_executions():
    """Reset execution state between tests (but keep flow definitions)"""
    yield
    # Only clear executions, not flow definitions
    flow_engine.executions.clear()
