import requests
import json
import os

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

SHOP_URL = os.getenv('SHOP_URL')
ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')
API_VERSION = "2023-10"
API_URL = f'{SHOP_URL}/admin/api/{API_VERSION}'
HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": ACCESS_TOKEN
}

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