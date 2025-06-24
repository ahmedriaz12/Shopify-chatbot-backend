# Import the functions from content_load.py
from content_load import load_context

# Import the fetch_order_data function from order_data.py
from order_data import fetch_order_data

# Import the save_chat_history function from chat_history.py
from chat_history import save_chat_history

# Import the ask_gemini function from gemini_interaction.py
from gemini_interaction import ask_gemini

from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from threading import Thread
import nest_asyncio
import uvicorn

# Allow FastAPI to run inside Jupyter
nest_asyncio.apply()

app = FastAPI()

# ✅ Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific domains in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str
    order_name: Optional[str] = None
    session_id: Optional[str] = None
    store_id: Optional[int] = None
    last_five_messages: Optional[list] = None

@app.post("/ask")
async def ask_customer_question(
    payload: QuestionRequest,
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    question = payload.question
    order_name = payload.order_name
    store_id = payload.store_id
    session_id = x_session_id or payload.session_id
    last_five_messages = payload.last_five_messages

    if not store_id:
        return {"response": "❌ Missing store_id. Please include it in the request."}
    
    if session_id:
        print(f"📝 Session ID received: {session_id}")

    try:
        base_context = load_context(store_id)
    except Exception as e:
        return {"response": f"❌ Failed to load store context: {str(e)}"}

    # Prepare conversation history
    history_context = "\n".join([f"{msg['type'].capitalize()}: {msg['content']}" for msg in last_five_messages]) if last_five_messages else "🕘 No session history available."
    # print(history_context)
    if order_name:
        order_context = fetch_order_data(order_name)
        full_context = f"{base_context}\n\n🚚 ORDER CONTEXT:\n{order_context}"
        response = ask_gemini(question, full_context, session_id, history_context)
    else:
        response = ask_gemini(question, base_context, session_id, history_context)

    # Save chat history if we have a session ID and response
    if session_id and response:
        save_chat_history(session_id, question, response, store_id)

    return {"response": response}

@app.get("/")
def read_root():
    return {"message": "Shopify Gemini Chatbot API is running."}

def start():
    uvicorn.run(app, host="0.0.0.0", port=8006, loop="asyncio", use_colors=True)

Thread(target=start).start()
