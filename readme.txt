# Shopify Gemini Chatbot Backend

A FastAPI-based backend for a Shopify chatbot that leverages Google Gemini for conversational AI. Integrates with MongoDB for data storage and Shopify's API for order data. The chatbot can answer customer questions, fetch order details, and maintain chat history.

---

## Features
- Conversational AI for Shopify stores using Google Gemini
- Fetches and presents product, page, and order data
- Handles order tracking and checkout link generation
- Maintains session-based chat history in MongoDB
- Strict privacy and response formatting rules
- CORS enabled for frontend integration

---

## Setup Instructions

1. **Clone the repository**
2. **Install dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Configure environment variables:**
   Create a `.env` file in the root directory with the following:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   SHOP_URL=https://yourshopifystore.com
   SHOPIFY_ACCESS_TOKEN=your_shopify_access_token
   MONGO_URI=your_mongodb_connection_string
   ```
4. **Start the server:**
   ```bash
   python main.py
   ```
   The API will run on `http://0.0.0.0:8006/`

---

## API Endpoints

### `POST /ask`
- **Description:** Ask a question as a customer. Handles context, order lookup, and chat history.
- **Request Body:**
  ```json
  {
    "question": "string",
    "order_name": "string (optional)",
    "session_id": "string (optional)",
    "store_id": 123,
    "last_five_messages": [ {"type": "user|bot", "content": "string"} ]
  }
  ```
- **Headers:**
  - `X-Session-ID` (optional): Session identifier
- **Response:**
  ```json
  { "response": "string" }
  ```

### `GET /`
- **Description:** Health check endpoint.
- **Response:**
  ```json
  { "message": "Shopify Gemini Chatbot API is running." }
  ```

---

## Environment Variables
- `GEMINI_API_KEY`: Google Gemini API key
- `SHOP_URL`: Shopify store URL
- `SHOPIFY_ACCESS_TOKEN`: Shopify API access token
- `MONGO_URI`: MongoDB connection string

---

## Dependencies
- fastapi
- uvicorn
- pymongo
- dotenv
- requests
- nest_asyncio
- pydantic

---

## Notes
- CORS is enabled for all origins (update for production!)
- Ensure MongoDB and Shopify credentials are correct
- For production, use a process manager (e.g., gunicorn) and secure environment variables

---
