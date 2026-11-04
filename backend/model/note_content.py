from pydantic import BaseModel

class NoteContent(BaseModel):
    title: str
    summary: str
    date_direction:str