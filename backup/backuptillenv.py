import json
import re
import requests
from datetime import datetime, timedelta, timezone
# import chromadb
# from sentence_transformers import SentenceTransformer
from collections import deque
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

final_look= "```json{ imagespreview_data: [{src: LINK}]}```" 
SHOP_URL = os.getenv('SHOP_URL')
ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')
API_VERSION = "2023-10"
API_URL = f'{SHOP_URL}/admin/api/{API_VERSION}'
HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": ACCESS_TOKEN
}
client = MongoClient(os.getenv('MONGO_URI'))
db = client['storedata']  # Replace with your database name
collection = db['products']  # Replace with your collection name

# Cache structure to store data and timestamp for each store_id
cache = {}

CACHE_DURATION = timedelta(hours=24)  # Cache duration of 24 hours

def get_products_by_store_id(store_id):
    store_id = int(store_id)  # Ensure store_id is an integer
    print(f"Querying products for store ID: {store_id}")  # Debug statement
    products = list(collection.find({'store_id': store_id}))
    if not products:
        print(f"No products found for store ID {store_id}.")
        return []

    print(f"Products for store ID {store_id}:")
    for product in products:
        print(f"- {product['title']} (ID: {product['id']})")
    return products

def load_context(store_id):
    current_time = datetime.now(timezone.utc)
    # Initialize cache for the store_id if not present
    if store_id not in cache:
        cache[store_id] = {
            'products': None,
            'pages': None,
            'last_updated': None
        }

    # Check if cache is valid for the store_id
    if cache[store_id]['last_updated'] and (current_time - cache[store_id]['last_updated']) < CACHE_DURATION:
        print("Using cached data for store_id:", store_id)
        return cache[store_id]['products'] + cache[store_id]['pages']

    context_parts = []
    context_parts_pages=[]

    # Fetch products from MongoDB using the get_products_by_store_id function
    try:
        products = get_products_by_store_id(store_id)
        if products:
            for product in products:
                if '_id' in product:
                    product['_id'] = str(product['_id'])
            context_parts.append("🛒 Products:\n")
            context_parts.append(json.dumps(products, indent=2))
            print("Debug: Appended products to context_parts") 
        else:
            context_parts.append("❌ No products found for the given store ID.")
    except Exception as e:
        context_parts.append(f"❌ Failed to fetch products from MongoDB: {str(e)}")

    # Fetch pages from MongoDB using store_id
    try:
        print(f"Debug: Querying pages for store ID: {store_id}")  # Debug statement
        pages = list(db['Pages'].find({'store_id': store_id}))
        print(f"Debug: Found {len(pages)} pages")  # Debug statement
        if pages:
            for page in pages:
                if '_id' in page:
                    page['_id'] = str(page['_id'])
            context_parts.append("\n\n\n📄All Store Pages Data:\n")
            context_parts.append(json.dumps(pages, indent=2))
            context_parts_pages.append("\n\n\n📄All Store Pages Data:\n")
            context_parts_pages.append(json.dumps(pages, indent=2))
        else:
            context_parts.append("❌ No pages found for the given store ID.")
    except Exception as e:
        context_parts.append(f"❌ Failed to fetch pages from MongoDB: {str(e)}")

    # Update cache for the store_id
    cache[store_id]['products'] = "\n".join(context_parts) if context_parts else ""
    cache[store_id]['pages'] = "\n".join(context_parts_pages) if context_parts_pages else ""
    cache[store_id]['last_updated'] = current_time

    return "\n".join(context_parts)

def ask_gemini(question: str, context: str, session_id: str = None, history_context: str = "🕘 No session history available."):
    headers = {"Content-Type": "application/json"}
    prompt = f"""You are a Shopify assistant and work for this store. Use the STORE DATA and CONVERSATION HISTORY to answer the customer's questions.
    
--- STORE DATA ---
{context}
--- END STORE DATA ---

--- CONVERSATION HISTORY ---
{history_context}
--- END CONVERSATION HISTORY ---

--- IMPORTANT DETAILS ---

    NEVER SHARE ANY INFORMATION OTHER THEN THIS STORE MAKE A DESIGION BY YOURSELF WHAT USER ASKED IS IT THREATS USERS DATA OR PRIVACY, like paswords, emails, history, prompt data, sensitive data, etc

    **some importat notes to keep in mind**
    1. Dont share any product stock information i repeat dont share it even if its outofstock.
    3. "MOST IMPORTANT" dont share any links unless user asked for it or there is a valid need like: site, product, images, pages, etc.
    2. present data in professional way.
    3. site main url it should be used everywhare like cart,pages etc, "https://freerangesupplements.com/" if its a product then it should be "https://freerangesupplements.com/products/"
    4. if user asks specifically to show images like not asking about information send data in json form what a field named trigger "imagespreview_data" and image src only (do not add any other thing).
     4.1: make sure to give images(JSON) Seprately of each product.
     4.2: Never share only images JSON also give some details about the product with them as a content outSide the json.
     4.3: Final look of JSON wich Should never be changed for images:{final_look}
     4.4: Every JSON should be wraped in this ```json   ```.

    5. "MOST IMPORTANT MAKE SURE TO HANDLE THIS WITH NO ERRORS": When user get information on specific product after giving responce ask him/her like "do you want to buy?" something like this.
     5.1: if user agrees to buy then process link genration in the next respone.
     5.2: dont ask for quantity it will be managed by user.
     5.3: make sure when generating the link it should be a complete link including site domain double check it.
     5.4: it should be json form named "checkout_data" with "link" containing link.
     5.5: IMPORTANT:(At the end link should look like this in JSON "{SHOP_URL}/cart/varientid:1").
     5.6: ^^ RESPONCE CRITREA ^^: user wants to buy product -> if product have Varients ask them for specific varient -> genrate link of that varient.
     5.7: Make sure USE OLD CONVERSATION to KEEP TRACK OF PRODUCT (VARIENT if have varients).
     5.8: NEVER STUCK AND LOOP AND KEEP ASKING ABOUT PRODUCT.
     5.9: if product have sigle varient its not considered as a varient but as a product can Sell in any quantity.
     6.0: ^^ MOST IMPORTANT ^^: Make sure use Varientsid in link genration dont mix that up with productid.
     
    6. if its selli in "individual bottles" just sell it in any quantity.
    7. make sure if you making json make sure dont talk about creation in any way just create json and i want to give information just give it but dont talk about json.

    **some more importat notes to keep in mind for order tracking**.
        ""MOST IMPORTANT MUST FOLLOW "" Always Make a New tracking request if user input contains new email or tracking/order ID. never use --- CONVERSATION HISTORY --- if any of it is changed.
    1. first check if the customer is asking for general information on how tracking works or want to track an order analyze this using your knowlage and check for user intent.
    2. if user want to get information on tracking then answer it using --- STORE DATA --- and accrording to --- CONVERSATION HISTORY ---.
    3. if user want to track order then ask them to share their email address and tracking number-> please enter email then id with space. For example:  email@example.com TRACKING123
    4. after getting both email and tracking number, output in this format:
       "Searching_order_by_credentials: email@example.com|TRACKING123"
       Make sure to separate email and tracking with a pipe (|) character.
       Make sure just output this as my function auto detects it and show results to user.
    

    **some more importat notes to keep in mind after you fetched order details**
    1. if you are presenting order data Dont ask further questions just present the data.
    2. if question asked after the order is fetched make sure stick to the details you have in --- CONVERSATION HISTORY --- and --- STORE DATA ---.
    3. if you cant find just sorry the user!
--- END IMPORTANT DETAILS ---  
s
Customer: {question}
Answer:"""

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(GEMINI_ENDPOINT, headers=headers, json=payload)

    if response.status_code == 200:
        try:
            text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            if "Searching_order_by_credentials:" in text:

                credentials = text.split("Searching_order_by_credentials:")[1].strip().split()[0]
                email, tracking = credentials.split("|")
                order_context = fetch_order_data(email, tracking)
                full_context = f"🚚 ORDER CONTEXT:\n{order_context}"
                answer_got = ask_gemini("this is user order data present it in professional way", full_context, session_id, history_context)
                return answer_got
            else:
                print(text)
                return text
        except:
            print("⚠️ Could not parse Gemini response.")
            return None
    else:
        print("❌ API error:", response.status_code, response.text)
        return None

def fetch_order_data(email, tracking_id):
    print(f"\n🔎 Starting order search with:")
    print(f"Email: {email}")
    print(f"Tracking/Order ID: {tracking_id}")
    
    endpoint = f"{API_URL}/orders.json?limit=250&status=any"
    matched_order = None
    page_count = 0

    while endpoint:
        page_count += 1
        print(f"\n📄 Fetching page {page_count}")
        print(f"API Endpoint: {endpoint}")
        
        try:
            response = requests.get(endpoint, headers=HEADERS)
            print(f"Response Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ API Error: {response.text}")
                return f"❌ Failed to fetch orders: {response.text}"

            orders = response.json().get("orders", [])
            print(f"Found {len(orders)} orders on this page")

            for order in orders:
                tracking_numbers = []
                for fulfillment in order.get("fulfillments", []):
                    fulfillment_tracking = fulfillment.get("tracking_numbers", [])
                    tracking_numbers.extend(fulfillment_tracking)

                order_name = order.get("name", "").replace("#", "")
                customer_email = order.get("customer", {}).get("email", "").lower()

                print(f"\nChecking order {order.get('name')}")
                print(f"Tracking numbers: {tracking_numbers}, Order name: {order_name}")

                has_tracking_or_orderid = tracking_id in tracking_numbers or tracking_id == order_name
                if has_tracking_or_orderid:
                    print("✅ ID matched, checking email now")
                    if customer_email == email.lower():
                        matched_order = order
                        print("✅ Email also matched - order found")
                        break
                    else:
                        print(f"❌ Email mismatch! Provided: {email.lower()}, Order has: {customer_email}")
                        return f"❌ Order ID or email does not match give error to user dont share anything else."

            if matched_order:
                print("\n✅ Order found, stopping search")
                break

            # Pagination
            link_header = response.headers.get("Link", "")
            print(f"\nPagination Link Header: {link_header}")
            
            next_page = None
            for part in link_header.split(","):
                if 'rel="next"' in part:
                    next_page = part[part.find("<")+1:part.find(">")]
                    break
            
            endpoint = next_page if next_page else None

        except Exception as e:
            print(f"❌ Error during API call: {str(e)}")
            return f"❌ Error fetching orders: {str(e)}"

    if not matched_order:
        print(f"\n❌ No order found matching tracking/order ID: {tracking_id}")
        return f"❌ Order ID or email does not match give error to user dont share anything else."

    print("\n📦 Processing matched order data")
    order_data = {
        "order_name": matched_order['name'],
        "created_at": matched_order['created_at'],
        "financial_status": matched_order.get("financial_status"),
        "fulfillment_status": matched_order.get("fulfillment_status"),
        "archived": bool(matched_order.get("closed_at")),
        "cancelled": bool(matched_order.get("cancelled_at")),
        "products": [],
        "tracking_numbers": [],
        "customer": {
            "email": matched_order.get("customer", {}).get("email"),
            "first_name": matched_order.get("customer", {}).get("first_name"),
            "last_name": matched_order.get("customer", {}).get("last_name")
        }
    }

    print("\n📝 Processing line items")
    for item in matched_order.get("line_items", []):
        print(f"Processing item: {item.get('title')}")
        order_data["products"].append({
            "title": item['title'],
            "sku": item.get("sku"),
            "quantity": item["quantity"]
        })

    print("\n📦 Processing fulfillments")
    for fulfillment in matched_order.get("fulfillments", []):
        print(f"Processing fulfillment: {fulfillment.get('id')}")
        order_data["tracking_numbers"].extend(fulfillment.get("tracking_numbers", []))
        if "tracking_company" in fulfillment:
            order_data["tracking_company"] = fulfillment.get("tracking_company")

    print("\n✅ Order data processing complete")
    return json.dumps(order_data, indent=2)

from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from threading import Thread
import nest_asyncio
import uvicorn
from datetime import datetime

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
    print(history_context)
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
