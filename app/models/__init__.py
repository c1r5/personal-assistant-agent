from typing import Optional
from pydantic.main import BaseModel

class ConnectorRequest(BaseModel):
    content: str
    connector: Optional[str] = None

class AgentResponse(BaseModel):
    content: str
