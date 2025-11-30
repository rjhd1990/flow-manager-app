from fastapi import FastAPI
from app.api.routers.api import router


app = FastAPI(title="Flow Manager API", description="A generic flow execution engine for sequential task processing",version="1.0.0")
@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}

app.include_router(router, prefix="/flow")
