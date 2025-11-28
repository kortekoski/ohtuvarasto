"""Tests for Flask web application routes."""
import unittest
from app import app, warehouses, articles


class TestFlaskRoutes(unittest.TestCase):
    """Test cases for Flask routes."""

    def setUp(self):
        """Set up test client and clear warehouses before each test."""
        self.client = app.test_client()
        app.config["TESTING"] = True
        warehouses.clear()
        articles.clear()

    def tearDown(self):
        """Clear warehouses after each test."""
        warehouses.clear()
        articles.clear()

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
        self.assertIn(b"created successfully", response.data)

    def test_create_warehouse_duplicate_name(self):
        """Test that duplicate warehouse names are rejected."""
        self.client.post("/warehouses", data={
            "name": "Duplicate",
            "capacity": "50"
        })
        response = self.client.post("/warehouses", data={
            "name": "Duplicate",
            "capacity": "100"
        }, follow_redirects=True)
        # Original warehouse should remain unchanged
        self.assertAlmostEqual(warehouses["Duplicate"].tilavuus, 50)
        self.assertIn(b"already exists", response.data)

    def test_create_warehouse_empty_name(self):
        """Test that empty warehouse names are rejected."""
        response = self.client.post("/warehouses", data={
            "name": "",
            "capacity": "100"
        }, follow_redirects=True)
        self.assertEqual(len(warehouses), 0)
        self.assertIn(b"name is required", response.data)

    def test_create_warehouse_invalid_capacity(self):
        """Test that invalid capacity values are handled."""
        response = self.client.post("/warehouses", data={
            "name": "Invalid",
            "capacity": "not_a_number"
        }, follow_redirects=True)
        self.assertNotIn("Invalid", warehouses)
        self.assertIn(b"Invalid capacity", response.data)

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
        self.assertIn(b"Added", response.data)

    def test_add_to_nonexistent_warehouse(self):
        """Test adding to a warehouse that doesn't exist."""
        response = self.client.post("/warehouses/Nonexistent/add", data={
            "amount": "10"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Nonexistent", warehouses)
        self.assertIn(b"not found", response.data)

    def test_add_invalid_amount(self):
        """Test adding invalid amount to a warehouse."""
        self.client.post("/warehouses", data={
            "name": "Invalid Add",
            "capacity": "100"
        })
        response = self.client.post("/warehouses/Invalid Add/add", data={
            "amount": "not_a_number"
        }, follow_redirects=True)
        # Should remain at 0 since invalid amount is ignored
        self.assertAlmostEqual(warehouses["Invalid Add"].saldo, 0)
        self.assertIn(b"Invalid amount", response.data)

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
        self.assertIn(b"Removed", response.data)

    def test_remove_from_nonexistent_warehouse(self):
        """Test removing from a warehouse that doesn't exist."""
        response = self.client.post("/warehouses/Nonexistent/remove", data={
            "amount": "10"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Nonexistent", warehouses)
        self.assertIn(b"not found", response.data)

    def test_remove_invalid_amount(self):
        """Test removing invalid amount from a warehouse."""
        self.client.post("/warehouses", data={
            "name": "Invalid Remove",
            "capacity": "100"
        })
        self.client.post("/warehouses/Invalid Remove/add", data={
            "amount": "50"
        })
        response = self.client.post("/warehouses/Invalid Remove/remove", data={
            "amount": "not_a_number"
        }, follow_redirects=True)
        # Should remain at 50 since invalid amount is ignored
        self.assertAlmostEqual(warehouses["Invalid Remove"].saldo, 50)
        self.assertIn(b"Invalid amount", response.data)

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
        self.assertIn(b"deleted", response.data)

    def test_delete_nonexistent_warehouse(self):
        """Test deleting a warehouse that doesn't exist."""
        response = self.client.post("/warehouses/Nonexistent/delete",
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_create_article(self):
        """Test creating a new article."""
        response = self.client.post("/articles", data={
            "name": "Test Article",
            "size": "10"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test Article", articles)
        self.assertAlmostEqual(articles["Test Article"], 10)
        self.assertIn(b"created", response.data)

    def test_create_article_duplicate_name(self):
        """Test that duplicate article names are rejected."""
        self.client.post("/articles", data={
            "name": "Duplicate",
            "size": "5"
        })
        response = self.client.post("/articles", data={
            "name": "Duplicate",
            "size": "10"
        }, follow_redirects=True)
        self.assertAlmostEqual(articles["Duplicate"], 5)
        self.assertIn(b"already exists", response.data)

    def test_create_article_empty_name(self):
        """Test that empty article names are rejected."""
        response = self.client.post("/articles", data={
            "name": "",
            "size": "10"
        }, follow_redirects=True)
        self.assertEqual(len(articles), 0)
        self.assertIn(b"name is required", response.data)

    def test_create_article_invalid_size(self):
        """Test that invalid size values are handled."""
        response = self.client.post("/articles", data={
            "name": "Invalid",
            "size": "not_a_number"
        }, follow_redirects=True)
        self.assertNotIn("Invalid", articles)
        self.assertIn(b"Invalid size", response.data)

    def test_create_article_zero_size(self):
        """Test that zero size is rejected."""
        response = self.client.post("/articles", data={
            "name": "Zero Size",
            "size": "0"
        }, follow_redirects=True)
        self.assertNotIn("Zero Size", articles)
        self.assertIn(b"must be greater than 0", response.data)

    def test_delete_article(self):
        """Test deleting an article."""
        self.client.post("/articles", data={
            "name": "Delete Article",
            "size": "5"
        })
        self.assertIn("Delete Article", articles)
        response = self.client.post("/articles/Delete Article/delete",
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Delete Article", articles)
        self.assertIn(b"deleted", response.data)

    def test_add_article_to_warehouse(self):
        """Test adding an article to a warehouse."""
        self.client.post("/warehouses", data={
            "name": "Article Test WH",
            "capacity": "100"
        })
        self.client.post("/articles", data={
            "name": "Box",
            "size": "20"
        })
        response = self.client.post(
            "/warehouses/Article Test WH/add-article",
            data={"article": "Box"},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(warehouses["Article Test WH"].saldo, 20)
        self.assertIn(b"Added", response.data)

    def test_add_article_to_nonexistent_warehouse(self):
        """Test adding article to warehouse that doesn't exist."""
        self.client.post("/articles", data={
            "name": "Box",
            "size": "20"
        })
        response = self.client.post(
            "/warehouses/Nonexistent/add-article",
            data={"article": "Box"},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"not found", response.data)

    def test_add_nonexistent_article_to_warehouse(self):
        """Test adding nonexistent article to warehouse."""
        self.client.post("/warehouses", data={
            "name": "Test WH",
            "capacity": "100"
        })
        response = self.client.post(
            "/warehouses/Test WH/add-article",
            data={"article": "Nonexistent"},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"not found", response.data)

    def test_add_article_not_enough_space(self):
        """Test adding article when warehouse doesn't have enough space."""
        self.client.post("/warehouses", data={
            "name": "Small WH",
            "capacity": "10"
        })
        self.client.post("/articles", data={
            "name": "Big Box",
            "size": "20"
        })
        response = self.client.post(
            "/warehouses/Small WH/add-article",
            data={"article": "Big Box"},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(warehouses["Small WH"].saldo, 0)
        self.assertIn(b"Not enough space", response.data)
