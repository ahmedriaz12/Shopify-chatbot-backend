import json
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
import os

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

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