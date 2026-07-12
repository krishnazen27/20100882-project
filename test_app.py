import unittest

# --- Simulated Marketplace Application Code ---
class Marketplace:
    def __init__(self):
        self.listings = []

    def add_listing(self, item_name, price, category, is_logged_in=False):
        if not is_logged_in:
            raise PermissionError("User must be logged in to post an item.")
        
        listing = {"name": item_name, "price": price, "category": category}
        self.listings.append(listing)
        return True


# --- The Unit Test Suite ---
class TestMarketplaceClassifieds(unittest.TestCase):

    def setUp(self):
        """
        Runs BEFORE every individual test case.
        Provides a completely fresh instance of the application.
        """
        self.app = Marketplace()
        print("\n[setUp] Initialized fresh marketplace instance.")

    def tearDown(self):
        """
        Runs AFTER every individual test case.
        Used to clean up data structures, close open connections, or clear memory.
        """
        self.app.listings.clear()
        del self.app
        print("[tearDown] Cleaned up and deleted marketplace instance.")

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
    unittest.main()