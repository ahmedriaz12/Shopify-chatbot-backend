from pymongo import MongoClient
from datetime import datetime
import os

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

client = MongoClient(os.getenv('MONGO_URI'))
db = client['storedata']  # Replace with your database name


def save_chat_history(session_id: str, question: str, response: str, store_id: int):
    if not session_id:
        return

    # Connect to the MongoDB collection for chat history
    chat_collection = db['chat_history']  # Replace with your collection name

    # Format the chat entry
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    chat_entry = {
        "timestamp": timestamp,
        "question": question,
        "response": response
    }

    # Check if a document with the session ID already exists
    existing_chat = chat_collection.find_one({"session_id": session_id})

    if existing_chat:
        # Append the new chat entry to the existing document
        chat_collection.update_one(
            {"session_id": session_id},
            {"$push": {"chats": chat_entry}}
        )
    else:
        # Create a new document with the session ID, store ID, and the chat entry
        chat_collection.insert_one({
            "session_id": session_id,
            "store_id": store_id,
            "chats": [chat_entry]
        })

    print(f"💾 Chat history saved to MongoDB for session ID: {session_id} and store ID: {store_id}") 