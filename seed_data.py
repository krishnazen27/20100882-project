import urllib.request
import json
import random
import http.cookiejar

# API Base URL for your local classifieds portal
API_BASE = "http://127.0.0.1:5000/api"

# Sample pools for generating randomized listings
titles_by_category = {
    "Electronics": ["iPhone 13 Pro", "Sony WH-1000XM4 Headphones", "Mechanical Keyboard", "Dell 27-inch Monitor", "Nintendo Switch"],
    "Motors": ["2015 Ford Focus", "Honda Civic VTEC", "Yamaha YZF-R3 Motorcycle", "Used Vespa Scooter", "Roof Rack Carrier"],
    "Books": ["Introduction to Python", "Dune Hardcover Edition", "Sapiens", "Thinking, Fast and Slow", "Calculus: Early Transcendentals"],
    "Sports & Outdoors": ["Mountain Bike", "Yoga Mat", "Camping Tent 4-Person", "Wilson Tennis Racket", "Adjustable Dumbbells (Pair)"],
    "Furniture": ["IKEA Malm Desk", "Ergonomic Office Chair", "Wooden Coffee Table", "Leather 3-Seater Sofa", "Bedside Nightstand"],
    "Clothing": ["Vintage Leather Jacket", "Nike Air Max Sneakers", "Patagonia Fleece", "Designer Sunglasses", "Waterproof Raincoat"]
}

# Seed accounts to register and build session states with
seed_users = ["Sivak", "Alice", "John", "Emma", "Liam", "Sophia", "Michael", "Chloe"]
domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.ie"]

# Setup a global cookie handler to automatically store session cookies across requests
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
urllib.request.install_opener(opener)

def register_and_login_users():
    """Registers all seed accounts and keeps track of authentication parameters."""
    print("Initializing user database registration and mapping sessions...")
    for user in seed_users:
        contact_info = f"{user.lower()}26@{random.choice(domains)}"
        password = f"password_{user.lower()}"
        
        # 1. Register Account
        reg_payload = json.dumps({
            "username": user,
            "password": password,
            "contact_info": contact_info
        }).encode('utf-8')
        
        reg_req = urllib.request.Request(
            f"{API_BASE}/auth/register",
            data=reg_payload,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(reg_req, timeout=3) as response:
                pass
        except Exception:
            # If user already exists (409), just ignore and proceed
            pass

def post_ad_as_user(username, payload):
    """Logs in as a specific user to grab a session cookie, then posts the ad."""
    password = f"password_{username.lower()}"
    login_payload = json.dumps({"username": username, "password": password}).encode('utf-8')
    
    # 1. Login to set session state
    login_req = urllib.request.Request(
        f"{API_BASE}/auth/login",
        data=login_payload,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(login_req, timeout=3) as login_res:
            if login_res.status != 200:
                return False
    except Exception as e:
        print(f"[Auth Error] Could not authenticate session for {username}: {e}")
        return False

    # 2. Post Listing (Cookie Jar automatically appends the login session cookie)
    ad_data = json.dumps(payload).encode('utf-8')
    ad_req = urllib.request.Request(
        f"{API_BASE}/listings",
        data=ad_data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(ad_req, timeout=3) as response:
            if response.status == 201:
                res_body = json.loads(response.read().decode())
                custom_id = res_body.get('dcm_id', 'N/A')
                print(f"[Success] Created Listing {custom_id}: {payload['title']} (€{payload['price_eur']}) in [{payload['category']}] by {username}")
                return True
    except Exception as e:
        print(f"[Error] Failed to post item: {e}")
        return False

def generate_random_listing():
    category = random.choice(list(titles_by_category.keys()))
    title = random.choice(titles_by_category[category])
    
    if random.choice([True, False]):
        title = f"Used {title}"
    else:
        title = f"{title} (Excellent Condition)"

    if category == "Motors":
        price_eur = round(random.uniform(150.0, 4500.0), 2)
    else:
        price_eur = round(random.uniform(10.0, 600.0), 2)

    return {
        "title": title,
        "category": category,
        "price_eur": price_eur
    }

def seed_database(count=10):
    register_and_login_users()
    print(f"\nStarting to inject {count} authenticated listings into the portal...\n")
    
    for _ in range(count):
        payload = generate_random_listing()
        random_seller = random.choice(seed_users)
        post_ad_as_user(random_seller, payload)

if __name__ == "__main__":
    seed_database(count=12)