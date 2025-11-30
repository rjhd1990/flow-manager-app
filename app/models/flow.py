from pydantic import BaseModel
class FlowRunResponse(BaseModel):
    id: str
    name: str
    status: str
    