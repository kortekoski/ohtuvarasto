"""Tests for Flask web application routes."""
import unittest
from app import app, warehouses


class TestFlaskRoutes(unittest.TestCase):
    """Test cases for Flask routes."""

    def setUp(self):
        """Set up test client and clear warehouses before each test."""
        self.client = app.test_client()
        app.config["TESTING"] = True
        warehouses.clear()

    def tearDown(self):
        """Clear warehouses after each test."""
        warehouses.clear()

    def test_index_redirects_to_warehouses(self):
        """Test that index route redirects to warehouses list."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/warehouses", response.location)

    def test_list_warehouses_empty(self):
        """Test listing warehouses when none exist."""
        response = self.client.get("/warehouses")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No warehouses yet", response.data)

    def test_create_warehouse(self):
        """Test creating a new warehouse."""
        response = self.client.post("/warehouses", data={
            "name": "Test Warehouse",
            "capacity": "100"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test Warehouse", warehouses)
        self.assertAlmostEqual(warehouses["Test Warehouse"].tilavuus, 100)

    def test_create_warehouse_duplicate_name(self):
        """Test that duplicate warehouse names are rejected."""
        self.client.post("/warehouses", data={
            "name": "Duplicate",
            "capacity": "50"
        })
        self.client.post("/warehouses", data={
            "name": "Duplicate",
            "capacity": "100"
        })
        # Original warehouse should remain unchanged
        self.assertAlmostEqual(warehouses["Duplicate"].tilavuus, 50)

    def test_create_warehouse_empty_name(self):
        """Test that empty warehouse names are rejected."""
        self.client.post("/warehouses", data={
            "name": "",
            "capacity": "100"
        })
        self.assertEqual(len(warehouses), 0)

    def test_create_warehouse_invalid_capacity(self):
        """Test that invalid capacity values are handled."""
        self.client.post("/warehouses", data={
            "name": "Invalid",
            "capacity": "not_a_number"
        })
        self.assertNotIn("Invalid", warehouses)

    def test_list_warehouses_with_items(self):
        """Test listing warehouses when some exist."""
        self.client.post("/warehouses", data={
            "name": "Warehouse A",
            "capacity": "50"
        })
        self.client.post("/warehouses", data={
            "name": "Warehouse B",
            "capacity": "100"
        })
        response = self.client.get("/warehouses")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Warehouse A", response.data)
        self.assertIn(b"Warehouse B", response.data)

    def test_add_to_warehouse(self):
        """Test adding content to a warehouse."""
        self.client.post("/warehouses", data={
            "name": "Add Test",
            "capacity": "100"
        })
        response = self.client.post("/warehouses/Add Test/add", data={
            "amount": "30"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(warehouses["Add Test"].saldo, 30)

    def test_add_to_nonexistent_warehouse(self):
        """Test adding to a warehouse that doesn't exist."""
        response = self.client.post("/warehouses/Nonexistent/add", data={
            "amount": "10"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Nonexistent", warehouses)

    def test_add_invalid_amount(self):
        """Test adding invalid amount to a warehouse."""
        self.client.post("/warehouses", data={
            "name": "Invalid Add",
            "capacity": "100"
        })
        self.client.post("/warehouses/Invalid Add/add", data={
            "amount": "not_a_number"
        })
        # Should remain at 0 since invalid amount is ignored
        self.assertAlmostEqual(warehouses["Invalid Add"].saldo, 0)

    def test_remove_from_warehouse(self):
        """Test removing content from a warehouse."""
        self.client.post("/warehouses", data={
            "name": "Remove Test",
            "capacity": "100"
        })
        self.client.post("/warehouses/Remove Test/add", data={
            "amount": "50"
        })
        response = self.client.post("/warehouses/Remove Test/remove", data={
            "amount": "20"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(warehouses["Remove Test"].saldo, 30)

    def test_remove_from_nonexistent_warehouse(self):
        """Test removing from a warehouse that doesn't exist."""
        response = self.client.post("/warehouses/Nonexistent/remove", data={
            "amount": "10"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Nonexistent", warehouses)

    def test_remove_invalid_amount(self):
        """Test removing invalid amount from a warehouse."""
        self.client.post("/warehouses", data={
            "name": "Invalid Remove",
            "capacity": "100"
        })
        self.client.post("/warehouses/Invalid Remove/add", data={
            "amount": "50"
        })
        self.client.post("/warehouses/Invalid Remove/remove", data={
            "amount": "not_a_number"
        })
        # Should remain at 50 since invalid amount is ignored
        self.assertAlmostEqual(warehouses["Invalid Remove"].saldo, 50)

    def test_delete_warehouse(self):
        """Test deleting a warehouse."""
        self.client.post("/warehouses", data={
            "name": "Delete Test",
            "capacity": "100"
        })
        self.assertIn("Delete Test", warehouses)
        response = self.client.post("/warehouses/Delete Test/delete",
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Delete Test", warehouses)

    def test_delete_nonexistent_warehouse(self):
        """Test deleting a warehouse that doesn't exist."""
        response = self.client.post("/warehouses/Nonexistent/delete",
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
