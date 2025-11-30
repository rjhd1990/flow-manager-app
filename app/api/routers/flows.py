import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_flow_engine
from app.models import FlowDefinition, FlowExecutionStatus
from app.services import FlowEngine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/flows", tags=["flows"])


@router.post("/register", status_code=201)
async def register_flow(
    flow_def: FlowDefinition, engine: FlowEngine = Depends(get_flow_engine)
):
    """Register a new flow definition"""
    try:
        engine.register_flow(flow_def)
        logger.info(f"Flow registered: {flow_def.flow.id}")
        return {
            "message": "Flow registered successfully",
            "flow_id": flow_def.flow.id,
            "flow_name": flow_def.flow.name,
        }
    except Exception as e:
        logger.error(f"Failed to register flow: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{flow_id}/execute")
async def execute_flow(flow_id: str, engine: FlowEngine = Depends(get_flow_engine)):
    """Execute a registered flow"""
    try:
        execution_id = engine.execute_flow(flow_id)
        execution = engine.get_execution_status(execution_id)
        logger.info(f"Flow execution started: {execution_id}")
        return {
            "message": "Flow execution completed",
            "execution_id": execution_id,
            "status": execution,
        }
    except Exception as e:
        logger.error(f"Failed to execute flow: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/execution/{execution_id}", response_model=FlowExecutionStatus)
async def get_execution_status(
    execution_id: str, engine: FlowEngine = Depends(get_flow_engine)
):
    """Get the status of a flow execution"""
    try:
        status = engine.get_execution_status(execution_id)
        return status
    except Exception as e:
        logger.error(f"Execution not found: {execution_id}")
        raise HTTPException(status_code=404, detail=str(e))


@router.get("")
async def list_flows(engine: FlowEngine = Depends(get_flow_engine)):
    """List all registered flows"""
    flows = engine.list_flows()
    return {"flows": flows, "count": len(flows)}
