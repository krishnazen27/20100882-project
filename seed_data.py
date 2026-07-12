import urllib.request
import json

API_BASE = "http://127.0.0.1:5000/api"

def register_and_login_users():
    print("Initializing user database registration and mapping sessions...")
    # TODO: wire this up to the real /api/auth/register endpoint

def seed_database(count=10):
    register_and_login_users()
    print(f"Would inject {count} listings into the portal...")

if __name__ == "__main__":
    seed_database(count=12)