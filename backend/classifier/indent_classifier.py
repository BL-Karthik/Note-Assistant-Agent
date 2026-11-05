

def classify_intent(messege:str)->str:

    return "NOTE" if "note" in messege else "QUERY"





def detect_intent(message: str) -> str:

    message = message.lower().strip()

    dbms_keywords = [
        "how many meetings",
        "total number of meetings",
        "count meetings",
        "number of meetings",

        "list all meetings",
        "list meetings",
        "show all meetings",
        "show me all meetings",
        "show meetings",
        "display meetings",

        "upcoming meetings",
        "future meetings",
        "scheduled meetings",
        "completed meetings",

        "yesterday meetings",
        "today meetings",
        "tomorrow meetings",
        "meetings yesterday",
        "meetings today",
        "meetings tomorrow",

        "meetings this week",
        "meetings next week",
        "meetings with",
        "meeting on"
    ]

    if any(keyword in message for keyword in dbms_keywords):
        return "DBMS_QUERY"

    return "SEMANTIC_QUERY"
