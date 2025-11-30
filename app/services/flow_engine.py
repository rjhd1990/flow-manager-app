import logging
import uuid
from datetime import UTC, datetime
from typing import Dict, Optional

from app.models import (
    Condition,
    Flow,
    FlowDefinition,
    FlowExecutionStatus,
    TaskResult,
    TaskStatus,
)
from app.services.task_registry import TaskRegistry

logger = logging.getLogger(__name__)


class FlowEngine:
    """Core flow execution engine"""

    def __init__(self, task_registry: TaskRegistry):
        self.task_registry = task_registry
        self.flow_definitions: Dict[str, Flow] = {}
        self.executions: Dict[str, FlowExecutionStatus] = {}

    def register_flow(self, flow_def: FlowDefinition):
        """Register a flow definition"""
        flow = flow_def.flow

        # Validate flow
        self._validate_flow(flow)

        self.flow_definitions[flow.id] = flow
        logger.info(f"Registered flow: {flow.name} (ID: {flow.id})")

    def _validate_flow(self, flow: Flow):
        """Validate flow definition"""
        # Check start task exists
        task_names = [t.name for t in flow.tasks]
        if flow.start_task not in task_names:
            raise ValueError(f"Start task '{flow.start_task}' not found in tasks")

        # Check all condition source tasks exist
        for condition in flow.conditions:
            if condition.source_task not in task_names:
                raise ValueError(
                    f"Condition source task '{condition.source_task}' not found"
                )

        logger.debug(f"Flow validation passed: {flow.name}")

    def execute_flow(self, flow_id: str) -> str:
        """Execute a flow and return execution ID"""
        if flow_id not in self.flow_definitions:
            raise ValueError(f"Flow '{flow_id}' not found")

        flow = self.flow_definitions[flow_id]
        execution_id = str(uuid.uuid4())

        # Initialize execution status
        execution = FlowExecutionStatus(
            execution_id=execution_id,
            flow_id=flow_id,
            status="running",
            current_task=flow.start_task,
            completed_tasks=[],
            task_results={},
            started_at=datetime.now(UTC).isoformat(),
        )

        self.executions[execution_id] = execution

        # Execute flow
        self._run_flow(execution, flow)

        return execution_id

    def _run_flow(self, execution: FlowExecutionStatus, flow: Flow):
        """Main flow execution loop with proper failure handling"""
        current_task = flow.start_task
        context = {}

        logger.info(f"Starting flow execution: {flow.name} ({execution.execution_id})")

        while current_task != "end":
            logger.info(f"Executing task: {current_task}")
            execution.current_task = current_task

            try:
                # Execute task
                task_func = self.task_registry.get(current_task)
                result = task_func(context)

                # Store result
                context[current_task] = result.model_dump()
                execution.task_results[current_task] = result
                execution.completed_tasks.append(current_task)

                logger.info(
                    f"Task {current_task} completed with status: {result.status}"
                )

                # Find and evaluate condition
                condition = self._find_condition(flow, current_task)

                if not condition:
                    logger.info(f"No condition for task {current_task}, ending flow")
                    break

                # Evaluate condition based on task result
                next_task = self._evaluate_condition(condition, result)
                logger.info(f"Condition evaluated: next task = {next_task}")

                # If next task is "end", we're done
                if next_task == "end":
                    logger.info("Flow directed to end")
                    break

                current_task = next_task

            except Exception as e:
                # Handle unexpected errors during task execution
                logger.error(
                    f"Unexpected error executing task {current_task}: {str(e)}"
                )
                execution.status = "failed"
                execution.current_task = None
                execution.ended_at = datetime.now(UTC).isoformat()
                execution.message = f"Flow failed at task {current_task}: {str(e)}"
                return

        # Determine final status based on completed tasks
        final_status = "completed"
        final_message = (
            f"Flow completed. Executed {len(execution.completed_tasks)} tasks."
        )

        # Check if any task failed
        failed_tasks = [
            task_name
            for task_name, result in execution.task_results.items()
            if result.status == TaskStatus.FAILURE
        ]

        if failed_tasks:
            final_status = "completed_with_failures"
            final_message = (
                f"Flow completed with failures. "
                f"Executed {len(execution.completed_tasks)} tasks. "
                f"Failed tasks: {', '.join(failed_tasks)}"
            )

        # Update execution status
        execution.status = final_status
        execution.current_task = None
        execution.ended_at = datetime.now(UTC).isoformat()
        execution.message = final_message

        logger.info(
            f"Flow execution finished: {execution.execution_id} - {final_status}"
        )

    def _find_condition(self, flow: Flow, task_name: str) -> Optional[Condition]:
        """Find condition for a given task"""
        for condition in flow.conditions:
            if condition.source_task == task_name:
                return condition
        return None

    def _evaluate_condition(self, condition: Condition, result: TaskResult) -> str:
        """Evaluate condition and return next task"""
        if result.status.value == condition.outcome:
            return condition.target_task_success
        else:
            return condition.target_task_failure

    def get_execution_status(self, execution_id: str) -> FlowExecutionStatus:
        """Get execution status"""
        if execution_id not in self.executions:
            raise ValueError(f"Execution '{execution_id}' not found")
        return self.executions[execution_id]

    def list_flows(self) -> list:
        """List all registered flows"""
        return [
            {
                "id": flow.id,
                "name": flow.name,
                "start_task": flow.start_task,
                "task_count": len(flow.tasks),
                "condition_count": len(flow.conditions),
            }
            for flow in self.flow_definitions.values()
        ]
