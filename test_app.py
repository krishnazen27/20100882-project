import unittest
import json
import os
from app import app, init_db

TEST_DB_FILE = 'test_classifieds.db'

class MarketplaceTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        if os.path.exists(TEST_DB_FILE):
            os.remove(TEST_DB_FILE)
        # Start every test from a clean schema
        init_db()
        self.app.post('/api/auth/register', data=json.dumps({
            "username": "testuser", "password": "password123", "contact_info": "test@domain.com"
        }), content_type='application/json')
        self.app.post('/api/auth/login', data=json.dumps({
            "username": "testuser", "password": "password123"
        }), content_type='application/json')

    def tearDown(self):
        if os.path.exists(TEST_DB_FILE):
            os.remove(TEST_DB_FILE)

    def test_add_marketplace_ad(self):
        """UNIT TEST: Verifies clean creation of a marketplace entry under an authenticated account."""
        payload = {"title": "Engineering Textbook", "category": "Books", "price_eur": 25.00}
        response = self.app.post('/api/listings', data=json.dumps(payload), content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", data)

if __name__ == '__main__':
    unittest.main(verbosity=2)