import unittest
import json
import os
from app import app, init_db

TEST_DB_FILE = 'test_classifieds.db'

class RequirementsTestCase(unittest.TestCase):

    def setUp(self):
        """Sets up a clean, isolated database and test client before each test."""
        app.config['TESTING'] = True
        self.app = app.test_client()
        
        if os.path.exists(TEST_DB_FILE):
            os.remove(TEST_DB_FILE)
            
        init_db()
        
        self.register_and_login_helper("test_user", "pass123")

    def tearDown(self):
        """Removes the temporary test database after each test completes."""
        if os.path.exists(TEST_DB_FILE):
            os.remove(TEST_DB_FILE)

    def register_and_login_helper(self, user, pwd):
        """Simulates authentication handshake."""
        self.app.post('/api/auth/register', data=json.dumps({
            "username": user, "password": pwd, "contact_info": "tester@example.com"
        }), content_type='application/json')
        
        self.app.post('/api/auth/login', data=json.dumps({
            "username": user, "password": pwd
        }), content_type='application/json')

    def test_crud_lifecycle(self):
        """
        UNIT TEST: Verifies the complete CRUD lifecycle of a listing.
        - Create: POST /api/listings
        - Read: GET /api/listings
        - Update: PUT /api/listings/<id>
        - Delete: DELETE /api/listings/<id>
        """
        new_item = {
            "title": "Test Bicycle",
            "category": "Sports & Outdoors",
            "price_eur": 150.00
        }
        create_response = self.app.post('/api/listings', data=json.dumps(new_item), content_type='application/json')
        self.assertEqual(create_response.status_code, 201)
        
        create_data = json.loads(create_response.data)
        self.assertIn("dcm_id", create_data)
        dcm_id = create_data["dcm_id"]

        read_response = self.app.get('/api/listings')
        self.assertEqual(read_response.status_code, 200)
        
        listings = json.loads(read_response.data)
        created_item = next((item for item in listings if item['dcm_id'] == dcm_id), None)
        self.assertIsNotNone(created_item)
        self.assertEqual(created_item['title'], "Test Bicycle")

        updated_payload = {
            "title": "Updated Test Bicycle",
            "category": "Sports & Outdoors",
            "price_eur": 130.00,
            "status": "Sold"
        }
        update_response = self.app.put(f'/api/listings/{dcm_id}', data=json.dumps(updated_payload), content_type='application/json')
        self.assertEqual(update_response.status_code, 200)
        
        check_res = self.app.get('/api/listings')
        current_listings = json.loads(check_res.data)
        verified_item = next(item for item in current_listings if item['dcm_id'] == dcm_id)
        self.assertEqual(verified_item['title'], "Updated Test Bicycle")
        self.assertEqual(verified_item['status'], "Sold")

        delete_response = self.app.delete(f'/api/listings/{dcm_id}')
        self.assertEqual(delete_response.status_code, 200)
        
        final_check_res = self.app.get('/api/listings')
        final_listings = json.loads(final_check_res.data)
        self.assertFalse(any(item['dcm_id'] == dcm_id for item in final_listings))

    def test_frontend_backend_integration(self):
        """
        INTEGRATION TEST: Assures the backend state coordinates and renders 
        dynamically into the frontend template templates/selling.html.
        """
        ui_response = self.app.get('/selling')
        self.assertEqual(ui_response.status_code, 200)
        
        self.assertIn(b"Post a New Used Item Ad", ui_response.data)
        self.assertIn(b"Your Current Managed Ads", ui_response.data)
        self.assertNotIn(b"Access Denied", ui_response.data)


if __name__ == '__main__':
    unittest.main(verbosity=2)