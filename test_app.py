import unittest
import json
import os
import re
from app import app, init_db

TEST_DB_FILE = 'test_classifieds.db'

class MarketplaceTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        if os.path.exists(TEST_DB_FILE):
            os.remove(TEST_DB_FILE)
        init_db()
        self.register_and_login_helper("testuser", "password123")

    def tearDown(self):
        if os.path.exists(TEST_DB_FILE):
            os.remove(TEST_DB_FILE)

    def register_and_login_helper(self, user, pwd):
        self.app.post('/api/auth/register', data=json.dumps({
            "username": user, "password": pwd, "contact_info": "test@domain.com"
        }), content_type='application/json')
        self.app.post('/api/auth/login', data=json.dumps({
            "username": user, "password": pwd
        }), content_type='application/json')

    def test_serve_buying_page(self):
        """VIEW TEST: Verifies root path successfully serves the Buying/Browse template."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Marketplace Dashboard", response.data)
        self.assertIn(b"Filter listings by ID, title, category, or seller", response.data)
    
    def test_serve_selling_page_authenticated(self):
        """VIEW TEST: Verifies /selling path renders management dashboard for logged-in sessions."""
        response = self.app.get('/selling')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Post a New Used Item Ad", response.data)
        self.assertIn(b"Your Current Managed Ads", response.data)

    def test_serve_profile_page(self):
        """VIEW TEST: Verifies /profile path serves the User Profile template details."""
        response = self.app.get('/profile')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Your Account Metadata Info", response.data)
        self.assertIn(b"Username Handle:", response.data)

    def test_add_marketplace_ad(self):
        """UNIT TEST: Verifies clean creation of an entry including description and custom dcm_id generation."""
        payload = {
            "title": "Engineering Textbook", 
            "category": "Books", 
            "price_eur": 25.00,
            "description": "Like new condition. No highlighting." 
        }
        response = self.app.post('/api/listings', data=json.dumps(payload), content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        
        self.assertIn("id", data)
        self.assertIn("dcm_id", data)
        
        self.assertTrue(re.match(r"^DCM-[A-Z0-9]{5}$", data["dcm_id"]))

    def test_missing_input_validation(self):
        """INTEGRITY TEST: Assures server rejects incomplete parameters."""
        payload = {"title": "Free Sofa"}
        response = self.app.post('/api/listings', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_buy_now_status_update(self):
        """FUNCTIONAL TEST: Verifies changing listing status to 'Sold' via simulated checkout (Buy Now)."""
        item = {"title": "Yamaha YZF-R3", "category": "Motors", "price_eur": 3200.00, "description": "Fast bike"}
        post_res = self.app.post('/api/listings', data=json.dumps(item), content_type='application/json')
        item_id = json.loads(post_res.data)['id']

        updated_payload = {"title": "Yamaha YZF-R3", "category": "Motors", "price_eur": 3200.00, "status": "Sold", "description": "Fast bike"}
        put_res = self.app.put(f'/api/listings/{item_id}', data=json.dumps(updated_payload), content_type='application/json')
        self.assertEqual(put_res.status_code, 200)

if __name__ == '__main__':
    unittest.main(verbosity=2)