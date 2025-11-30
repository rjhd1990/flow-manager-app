import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dependencies import flow_engine
from app.api.routers import flows_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.models import FlowDefinition

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A generic flow execution engine for sequential task processing",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


# Include routers
app.include_router(flows_router, prefix=settings.API_V1_PREFIX)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialization code
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Load default flow
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

    flow_def = FlowDefinition(**sample_flow)
    flow_engine.register_flow(flow_def)
    logger.info("Default flow loaded successfully")
    yield  # App runs here

    # Shutdown
    logger.info("Shutting down...")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"{settings.APP_NAME} v{settings.APP_VERSION}",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
