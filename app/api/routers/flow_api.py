from fastapi import APIRouter
from models.flow import FlowRunResponse

router = APIRouter()

@router.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Flow Manager API",
        "version": "1.0.0",
        "endpoints": {
            "POST /flow/register": "Register a new flow",
            "POST /flow/{flow_id}/execute": "Execute a flow",
            "GET /flow/execution/{execution_id}": "Get execution status",
            "GET /flows": "List all registered flows"
        }
    }

@router.post("/flow/register")
async def register_flow():
    """Register a new flow definition"""
    try:
    
    except Exception as e:
        raise HTTPException(status_code=400, detial=str(e))


@router.post("/flow/execute", response_model=FlowRunResponse)
async def run_flow(request )-> FlowRunResponse:
    pass

@router.get("/flow/{flow_id}/status")
async def get_flow_status(flow_id: str):
    pass



