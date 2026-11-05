from fastapi import FastAPI
from model.indent_request import IndentRequest
from classifier.indent_classifier import classify_intent
from service.summarizer import process_messege
from service.date_service import extract_meeting_date
from fastapi.middleware.cors import CORSMiddleware
from service.chroma_service import store_chunks_in_chroma ,retrieve_chunks_from_chroma
from config.chroma_config import client
from uuid import uuid4
from pathlib import Path

app=FastAPI(
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

@app.post("/classify")
def classify(request:IndentRequest):

    conversation_id=request.conversation_id
    if not conversation_id:
        conversation_id=f"chat--{uuid4().hex[:8]}"

    indent=classify_intent(request.messege.lower())
    if "NOTE"==indent:
        note_summary=process_messege(request.messege)
        result= store_chunks_in_chroma(note_summary)
        return{
            "conversation_id": conversation_id,
            "type": "NOTE",
            "result": result
        }


    result= retrieve_chunks_from_chroma(request.messege)
    return {
        "conversation_id": conversation_id,
        "type": "QUERY",
        "result": result
    }

@app.get("/test")
def test(): 
    collection=client.get_or_create_collection("note_chunks")
    return {"message":collection.get()}






