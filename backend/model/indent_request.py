from pydantic import BaseModel

from typing import Optional

class IndentRequest(BaseModel):
    messege:str
    conversation_id: Optional[str] = None