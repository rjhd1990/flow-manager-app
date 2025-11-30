import logging
import random
from typing import Dict

from app.models import TaskResult, TaskStatus

logger = logging.getLogger(__name__)


def task1_fetch_data(context: Dict) -> TaskResult:
    """Task 1: Fetch data"""
    try:
        # Check for forced failure in context
        if context.get("force_task1_failure"):
            raise Exception("Simulated fetch failure")

        # Simulate data fetching
        data = {"records": [1, 2, 3, 4, 5], "source": "database"}
        logger.info(f"Task1: Fetched {len(data['records'])} records")

        return TaskResult(
            status=TaskStatus.SUCCESS, data=data, message="Data fetched successfully"
        )
    except Exception as e:
        logger.error(f"Task1 failed: {str(e)}")
        return TaskResult(
            status=TaskStatus.FAILURE,
            data=None,
            message=f"Failed to fetch data: {str(e)}",
        )


def task2_process_data(context: Dict) -> TaskResult:
    """Task 2: Process data"""
    try:
        # Check for forced failure
        if context.get("force_task2_failure"):
            raise Exception("Simulated processing failure")

        # Get data from previous task
        previous_data = context.get("task1", {}).get("data", {})
        records = previous_data.get("records", [])

        if not records:
            raise ValueError("No records to process")

        # Simulate processing
        processed = [x * 2 for x in records]
        logger.info(f"Task2: Processed {len(processed)} records")

        return TaskResult(
            status=TaskStatus.SUCCESS,
            data={"processed_records": processed},
            message="Data processed successfully",
        )
    except Exception as e:
        logger.error(f"Task2 failed: {str(e)}")
        return TaskResult(
            status=TaskStatus.FAILURE,
            data=None,
            message=f"Failed to process data: {str(e)}",
        )


def task3_store_data(context: Dict) -> TaskResult:
    """Task 3: Store data"""
    try:
        # Check for forced failure
        if context.get("force_task3_failure"):
            raise Exception("Simulated storage failure")

        # Get data from previous task
        previous_data = context.get("task2", {}).get("data", {})
        processed_records = previous_data.get("processed_records", [])

        if not processed_records:
            raise ValueError("No processed records to store")

        # Simulate storing
        logger.info(f"Task3: Stored {len(processed_records)} records")

        return TaskResult(
            status=TaskStatus.SUCCESS,
            data={"stored_count": len(processed_records)},
            message="Data stored successfully",
        )
    except Exception as e:
        logger.error(f"Task3 failed: {str(e)}")
        return TaskResult(
            status=TaskStatus.FAILURE,
            data=None,
            message=f"Failed to store data: {str(e)}",
        )


def task_always_fails(context: Dict) -> TaskResult:
    """A task that always fails - for testing"""
    logger.error("Task designed to fail")
    return TaskResult(
        status=TaskStatus.FAILURE, data=None, message="This task always fails"
    )


def task_random_failure(context: Dict) -> TaskResult:
    """A task that randomly fails - for testing"""
    if random.random() < 0.5:
        logger.error("Task randomly failed")
        return TaskResult(
            status=TaskStatus.FAILURE, data=None, message="Random failure occurred"
        )
    else:
        logger.info("Task randomly succeeded")
        return TaskResult(
            status=TaskStatus.SUCCESS,
            data={"result": "success"},
            message="Task completed successfully",
        )
