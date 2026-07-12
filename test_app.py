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

    def test_add_success(self):
        """Case 1: Ensure logged-in users can successfully add an item."""
        print(" -> Running: test_add_success")
        result = self.app.add_listing(
            item_name="iPhone 15", 
            price=799.00, 
            category="Electronics", 
            is_logged_in=True
        )
        
        # Assertions
        self.assertTrue(result)
        self.assertEqual(len(self.app.listings), 1)
        self.assertEqual(self.app.listings[0]["name"], "iPhone 15")

    def test_add_unauthenticated_error(self):
        """Case 2: Ensure logged-out users are blocked from adding an item."""
        print(" -> Running: test_add_unauthenticated_error")
        # Assert that a PermissionError is raised when is_logged_in=False
        with self.assertRaises(PermissionError):
            self.app.add_listing(
                item_name="Vintage Jacket", 
                price=45.00, 
                category="Clothing", 
                is_logged_in=False
            )
        
        # Verify nothing was added to the registry
        self.assertEqual(len(self.app.listings), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)