import urllib.request
import json
import http.cookiejar
import random

# API Base URL for your local classifieds portal
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
    print("Initializing user database registration and mapping sessions...")
    # TODO: wire this up to the real /api/auth/register endpoint

def seed_database(count=10):
    register_and_login_users()
    print(f"Would inject {count} listings into the portal...")

if __name__ == "__main__":
    seed_database(count=12)