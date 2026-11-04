import json
from pathlib import Path

# Location of our JSON file
HISTORY_FILE = Path("app/data/conversation_history.json")


def load_conversations():

    with open(HISTORY_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data

def save_conversations(data):

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def create_conversation(conversation_id):

    data = load_conversations()

    conversation = {
        "conversation_id": conversation_id,
        "messages": []
    }

    data["conversations"].append(conversation)

    save_conversations(data)

    return conversation

def add_message(conversation_id, role, content):

    data = load_conversations()

    for conversation in data["conversations"]:

        if conversation["conversation_id"] == conversation_id:

            message = {
                "role": role,
                "content": content
            }

            conversation["messages"].append(message)

            save_conversations(data)

            return conversation

    return None