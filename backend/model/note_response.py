from pydantic import BaseModel

class NoteResponse(BaseModel):
    summary:str="No summary available"
