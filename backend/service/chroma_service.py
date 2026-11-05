
from config.chroma_config import client
from model.note_summary import NoteSummary
from service.chunking_Service import split_into_chunks
from model.note_response import NoteResponse
from service.summarizer import process_retrival_messege
from dateparser.search import search_dates
from classifier.indent_classifier import detect_intent


def store_chunks_in_chroma(note_summary: NoteSummary):

    text = note_summary.title + " " + note_summary.summary

    chunks = split_into_chunks(text)

    collection = client.get_or_create_collection("note_chunks")
    collection.add(
        ids=[f"{note_summary.note_id}_chunk_{i}" for i in range(len(chunks))],
        documents=chunks,
        metadatas=[
            {
                "note_id": note_summary.note_id,
                "meeting_date": str(note_summary.meeting_date),
                "title": note_summary.title
            }
            for i in range(len(chunks))
        ]
    )

    print("STORING NOTE:", note_summary.note_id)
    print("NOTE TITLE:", note_summary.title)
    print("NOTE SUMMARY:", note_summary.summary)
    print("CHUNKS:", chunks)

    return NoteResponse(summary=note_summary.summary)


def get_unique_notes(meeting_date: str = None):

    collection = client.get_or_create_collection("note_chunks")

    filters = {}
    if meeting_date:
        filters["where"] = {
            "meeting_date": meeting_date
        }

    results = collection.get(
        **filters,
        include=["documents", "metadatas"]
    )

    notes = {}

    # Group chunks using note_id
    for document, metadata in zip(results["documents"], results["metadatas"]):

        note_id = metadata["note_id"]

        if note_id not in notes:
            notes[note_id] = {
                "meeting_date": metadata.get("meeting_date"),
                "title": metadata.get("title"),
                "documents": []
            }

        notes[note_id]["documents"].append(document)

    return notes


def list_meetings(meeting_date: str = None):

    notes = get_unique_notes(meeting_date)

    return notes


def count_meetings(meeting_date: str = None):

    notes = get_unique_notes(meeting_date)

    return len(notes)


def retrieve_chunks_from_chroma(messege: str):

    indent = detect_intent(messege)
    print("Detected Intent:", indent)

    if indent == "COUNT":
        date = extract_date_from_query(messege)
        total = count_meetings(date)

        return NoteResponse(
            summary=f"You have {total} meetings recorded in your notes."
        )

    if indent == "LIST":
        date = extract_date_from_query(messege)
        meetings = list_meetings(date)

        meeting_list = ""

        for note_id, details in meetings.items():
            meeting_list += (
                f"Meeting: {details.get('title', 'No Title')}\n"
                f"Date: {details['meeting_date']}\n\n"
            )

        return NoteResponse(summary=meeting_list)

    # Semantic search: search across all notes without a date filter
    collection = client.get_or_create_collection("note_chunks")

    results = collection.query(
        query_texts=[messege],
        n_results=10,
        include=["documents", "metadatas", "distances"]
    )

    print("QUERY:", messege)
    print("DOCUMENTS:", results["documents"])
    print("METADATA:", results["metadatas"])
    print("DISTANCES:", results["distances"])

    content = results["documents"][0]
    metadata_list = results["metadatas"][0]

    retrived_text = ""

    for document, metadata in zip(content, metadata_list):
        retrived_text += (
            f"Meeting Date: {metadata['meeting_date']}\n"
            f"Content: {document}\n"
            f"Note ID: {metadata['note_id']}\n\n"
        )

    if not retrived_text:
        return NoteResponse(
            summary="I couldn't find this information in your meeting notes."
        )

    print("USER MESSAGE:", messege)
    print("RETRIEVED TEXT:", retrived_text)

    return process_retrival_messege(messege, retrived_text)


def extract_date_from_query(message: str):

    results = search_dates(
        message,
        settings={
            "TIMEZONE": "Asia/Kolkata",
            "RETURN_AS_TIMEZONE_AWARE": True,
        }
    )

    if results:
        extracted_date = results[0][1]
        return extracted_date.strftime("%Y-%m-%d")

    return None
