from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"
    RUNNING = "running"


class TaskResult(BaseModel):
    """Result returned by a task execution"""

    status: TaskStatus
    data: Optional[Any] = None
    message: Optional[str] = None


class Task(BaseModel):
    """Task definition"""

    name: str
    description: str


class Condition(BaseModel):
    """Condition that routes flow based on task outcome"""

    name: str
    description: str
    source_task: str
    outcome: str
    target_task_success: str
    target_task_failure: str


class Flow(BaseModel):
    """Flow definition"""

    id: str
    name: str
    start_task: str
    tasks: List[Task]
    conditions: List[Condition]


class FlowDefinition(BaseModel):
    """Wrapper for flow JSON"""

    flow: Flow


class FlowExecutionStatus(BaseModel):
    """Status of a flow execution"""

    execution_id: str
    flow_id: str
    status: str
    current_task: Optional[str] = None
    completed_tasks: List[str] = Field(default_factory=list)
    task_results: Dict[str, TaskResult] = Field(default_factory=dict)
    started_at: str
    ended_at: Optional[str] = None
    message: Optional[str] = None
