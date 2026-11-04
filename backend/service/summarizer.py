import os
from  dotenv import load_dotenv
from google import genai
from backend.model.note_summary import NoteSummary
from backend.model.note_content import NoteContent
from backend.prompts.prompt import NOTE_EXTRACTION_PROMPT 
from backend.prompts.retrival_prompt import RETRIVAL_EXTRACTION_PROMPT
from backend.service.date_service import extract_meeting_date
from backend.service.note_id_service import generate_note_id
from backend.model.note_response import NoteResponse
from datetime import date
from pathlib import Path

env_path = Path(__file__).resolve().parents[1] / ".env"

load_dotenv(dotenv_path=env_path)

client =genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def process_messege(user_message:str):

    prompt=f"""{NOTE_EXTRACTION_PROMPT}
               User message:{user_message} """

    response=client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type":"application/json",
            "response_schema":NoteContent
        }
    )

    result= NoteContent.model_validate_json(response.text)

    meeting_date=extract_meeting_date(user_message, result.date_direction)
    if meeting_date is None:
        meeting_date = date.today()
    
    print("USER MESSAGE:", user_message)
    print("GEMINI DATE DIRECTION:", result.date_direction)
    print("PYTHON EXTRACTED DATE:", meeting_date)

    note_id=generate_note_id()
    date_direction=result.date_direction

    

    return NoteSummary(
        title=result.title,
        summary=result.summary,
        date_direction=date_direction,
        meeting_date=meeting_date,
        note_id=note_id
    )


def process_retrival_messege(user_message: str, retrived_text: str):

    prompt = f"""
     {RETRIVAL_EXTRACTION_PROMPT}

      USER QUESTION:
    {user_message}

     RETRIEVED MEETING EVIDENCE:
    <meeting_notes>
      {retrived_text}
      </meeting_notes>

       INSTRUCTIONS:
       1. Find the meeting evidence directly relevant to the question.
       2. Identify the exact facts supporting the answer.
       3. Match broader concepts only when the notes support that relationship.
       4. Ignore unrelated meetings and information.
       5. If relevant evidence exists, answer using those facts.
       6. If no relevant evidence exists, return:
       I couldn't find this information in your meeting notes.

        Return only the structured response matching the required schema.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": NoteResponse
        }
    )

    result = NoteResponse.model_validate_json(response.text)

    print("USER QUESTION:", user_message)
    print("GENERATED ANSWER:", result.summary)

    return NoteResponse(summary=result.summary)






    