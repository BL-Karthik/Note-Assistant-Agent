
from uuid import uuid5, NAMESPACE_URL

from qdrant_client import models

from service.date_service import extract_meeting_date

from config.qdrant_config import (
    client,
    COLLECTION_NAME,
    EMBEDDING_MODEL
)

from model.note_summary import NoteSummary
from model.note_response import NoteResponse
from service.chunking_Service import split_into_chunks
from service.summarizer import process_retrival_messege
from dateparser.search import search_dates
from classifier.indent_classifier import detect_intent


def store_chunks_in_qdrant(note_summary: NoteSummary):

    text = note_summary.title + " " + note_summary.summary

    chunks = split_into_chunks(text)

    points = []

    for i, chunk in enumerate(chunks):

        point_id = str(
            uuid5(
                NAMESPACE_URL,
                f"{note_summary.note_id}_chunk_{i}"
            )
        )

        points.append(
            models.PointStruct(
                id=point_id,
                vector=models.Document(
                    text=chunk,
                    model=EMBEDDING_MODEL
                ),
                payload={
                    "note_id": note_summary.note_id,
                    "meeting_date": str(note_summary.meeting_date),
                    "title": note_summary.title,
                    "document": chunk
                }
            )
        )

    if points:
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
            wait=True
        )

    print("STORING NOTE:", note_summary.note_id)
    print("NOTE TITLE:", note_summary.title)
    print("CHUNKS:", chunks)

    return NoteResponse(summary=note_summary.summary)


def get_unique_notes(meeting_date: str = None):

    scroll_filter = None

    if meeting_date:
        scroll_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="meeting_date",
                    match=models.MatchValue(value=meeting_date)
                )
            ]
        )

    notes = {}
    offset = None

    while True:

        records, next_offset = client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=scroll_filter,
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=False
        )

        for record in records:

            metadata = record.payload or {}
            note_id = metadata.get("note_id")

            if not note_id:
                continue

            if note_id not in notes:
                notes[note_id] = {
                    "meeting_date": metadata.get("meeting_date"),
                    "title": metadata.get("title"),
                    "documents": []
                }

            document = metadata.get("document")

            if document:
                notes[note_id]["documents"].append(document)

        if next_offset is None:
            break

        offset = next_offset

    return notes


def list_meetings(meeting_date: str = None):

    return get_unique_notes(meeting_date)


def count_meetings(meeting_date: str = None):

    return len(get_unique_notes(meeting_date))


def retrieve_chunks_from_qdrant(messege: str):

    intent = detect_intent(messege)

    print("Detected Intent:", intent)

    # Structured database questions
    if intent == "DBMS_QUERY":

        message_lower = messege.lower()

        count_keywords = [
            "how many",
            "total number",
            "count",
            "number of meetings"
        ]

        list_keywords = [
            "list",
            "show",
            "display",
            "upcoming",
            "future",
            "scheduled",
            "completed",
            "meetings with",
            "meeting on"
        ]

        if any(keyword in message_lower for keyword in count_keywords):

            date = extract_date_from_query(messege)
            total = count_meetings(date)

            return NoteResponse(
                summary=f"You have {total} meetings recorded in your notes."
            )

        if any(keyword in message_lower for keyword in list_keywords):

            date = extract_date_from_query(messege)
            meetings = list_meetings(date)

            if not meetings:
                return NoteResponse(
                    summary="I couldn't find any meetings in your notes."
                )

            meeting_list = ""

            for note_id, details in meetings.items():

                meeting_list += (
                    f"Meeting: {details.get('title', 'No Title')}\n"
                    f"Date: {details.get('meeting_date')}\n\n"
                )

            return NoteResponse(summary=meeting_list)

    # Semantic search
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=models.Document(
            text=messege,
            model=EMBEDDING_MODEL
        ),
        limit=10,
        with_payload=True
    )

    retrieved_text = ""

    for point in results.points:

        metadata = point.payload or {}

        retrieved_text += (
            f"Meeting Date: {metadata.get('meeting_date')}\n"
            f"Content: {metadata.get('document', '')}\n"
            f"Note ID: {metadata.get('note_id')}\n\n"
        )

    if not retrieved_text:

        return NoteResponse(
            summary="I couldn't find this information in your meeting notes."
        )

    print("USER MESSAGE:", messege)
    print("RETRIEVED TEXT:", retrieved_text)

    return process_retrival_messege(messege, retrieved_text)





def extract_date_from_query(message: str):

    result = extract_meeting_date(message)

    if result is None:
        return None

    return result.strftime("%Y-%m-%d")
