from pydantic import BaseModel
from typing import Optional

class MLRequest(BaseModel):
    prompt: str
    context: Optional[dict] = {}

class MLResponse(BaseModel):
    response: str
    confidence: Optional[float] = None
    metadata: Optional[dict] = {}