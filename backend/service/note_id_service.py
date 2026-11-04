from datetime import datetime
from uuid import uuid4
from zoneinfo import ZoneInfo


def generate_note_id():
    today = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%y%m%d")

    unique_id = uuid4().hex[:8]

    return f"note-{today}-{unique_id}"