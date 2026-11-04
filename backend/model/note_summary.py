from pydantic import BaseModel
from typing import Literal
from datetime import date

class NoteSummary(BaseModel):
    note_id: str
    title: str
    summary: str
    meeting_date: date
    date_direction: Literal["PAST", "FUTURE", "TODAY", "NONE"]