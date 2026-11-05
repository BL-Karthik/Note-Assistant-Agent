
from fastapi import FastAPI
from model.indent_request import IndentRequest
from classifier.indent_classifier import classify_intent, detect_intent
from service.summarizer import process_messege
from fastapi.middleware.cors import CORSMiddleware

from service.qdrant_service import (
    store_chunks_in_qdrant,
    retrieve_chunks_from_qdrant,
    count_meetings,
    list_meetings,
    extract_date_from_query
)

from uuid import uuid4


app = FastAPI(
    title="Note Assistant Agent"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://note-assistant-agent-rho.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/classify")
@app.post("/classify")
def classify(request: IndentRequest):

    conversation_id = request.conversation_id

    if not conversation_id:
        conversation_id = f"chat--{uuid4().hex[:8]}"

    message = request.messege.strip()

    # Step 1: Check whether the message is a new NOTE
    intent = classify_intent(message.lower())

    if intent == "NOTE":

        note_summary = process_messege(message)

        result = store_chunks_in_qdrant(note_summary)

        return {
            "conversation_id": conversation_id,
            "type": "NOTE",
            "result": result
        }

    # Step 2: Identify the type of QUERY
    query_intent = detect_intent(message)

    # Step 3: Handle structured database queries
    if query_intent == "DBMS_QUERY":

        message_lower = message.lower()

        count_keywords = [
            "how many",
            "total number",
            "count",
            "number of meetings"
        ]

        if any(keyword in message_lower for keyword in count_keywords):

            date = extract_date_from_query(message)

            total = count_meetings(date)

            return {
                "conversation_id": conversation_id,
                "type": "QUERY",
                "result": {
                    "summary": f"You have {total} meetings recorded in your notes."
                }
            }

        date = extract_date_from_query(message)

        meetings = list_meetings(date)

        if not meetings:
            summary = "I couldn't find any meetings in your notes."
        else:
            meeting_details = []

            for note_id, meeting in meetings.items():
                meeting_details.append(
                    f"Title: {meeting['title']}, "
                    f"Date: {meeting['meeting_date']}"
                )

            summary = "\n".join(meeting_details)

        return {
            "conversation_id": conversation_id,
            "type": "QUERY",
            "result": {
                "summary": summary
            }
        }

    # Step 4: Handle semantic queries using Qdrant
    result = retrieve_chunks_from_qdrant(message)

    return {
        "conversation_id": conversation_id,
        "type": "QUERY",
        "result": result
    }
