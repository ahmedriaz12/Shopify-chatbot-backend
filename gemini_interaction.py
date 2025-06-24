import requests
import os
from order_data import fetch_order_data
# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
SHOP_URL = os.getenv('SHOP_URL')

final_look= "```json{ imagespreview_data: [{src: LINK}]}```" 


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