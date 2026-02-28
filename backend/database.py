"""
SQLite Database Layer for the Supermarket AI Assistant.
Handles all CRUD operations for products, aisles, and store configuration.
"""

import sqlite3
import os
import json

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "store.db")


def get_connection():
    """Get a database connection with row factory enabled."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initialize the database schema."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS store_config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS aisles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            section TEXT DEFAULT '',
            grid_x INTEGER NOT NULL,
            grid_y INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            brand TEXT DEFAULT '',
            category TEXT DEFAULT '',
            variants TEXT DEFAULT '[]',
            price REAL DEFAULT 0.0,
            quantity TEXT DEFAULT '',
            aisle_id INTEGER,
            shelf INTEGER DEFAULT 1,
            keywords TEXT DEFAULT '',
            FOREIGN KEY (aisle_id) REFERENCES aisles(id) ON DELETE SET NULL
        );
    """)

    # Set default store config
    defaults = {
        "store_name": "My Supermarket",
        "grid_rows": "6",
        "grid_cols": "5",
        "entrance_x": "0",
        "entrance_y": "0",
        "admin_password": "admin123"
    }
    for key, value in defaults.items():
        cursor.execute(
            "INSERT OR IGNORE INTO store_config (key, value) VALUES (?, ?)",
            (key, value)
        )

    conn.commit()
    conn.close()


# ── Store Config ──────────────────────────────────────────────────────

def get_config(key):
    conn = get_connection()
    row = conn.execute("SELECT value FROM store_config WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else None


def set_config(key, value):
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO store_config (key, value) VALUES (?, ?)",
        (key, str(value))
    )
    conn.commit()
    conn.close()


def get_all_config():
    conn = get_connection()
    rows = conn.execute("SELECT key, value FROM store_config").fetchall()
    conn.close()
    return {row["key"]: row["value"] for row in rows}


# ── Aisles ────────────────────────────────────────────────────────────

def add_aisle(name, section, grid_x, grid_y):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO aisles (name, section, grid_x, grid_y) VALUES (?, ?, ?, ?)",
        (name, section, grid_x, grid_y)
    )
    aisle_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return aisle_id


def update_aisle(aisle_id, name, section, grid_x, grid_y):
    conn = get_connection()
    conn.execute(
        "UPDATE aisles SET name=?, section=?, grid_x=?, grid_y=? WHERE id=?",
        (name, section, grid_x, grid_y, aisle_id)
    )
    conn.commit()
    conn.close()


def delete_aisle(aisle_id):
    conn = get_connection()
    conn.execute("DELETE FROM aisles WHERE id=?", (aisle_id,))
    conn.commit()
    conn.close()


def get_all_aisles():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM aisles ORDER BY name").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_aisle_by_id(aisle_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM aisles WHERE id=?", (aisle_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ── Products ──────────────────────────────────────────────────────────

def add_product(name, brand, category, variants, aisle_id, shelf, keywords, price=0.0, quantity=""):
    """Add a new product to the database."""
    conn = get_connection()
    variants_json = json.dumps(variants) if isinstance(variants, list) else variants
    cursor = conn.execute(
        """INSERT INTO products (name, brand, category, variants, price, quantity, aisle_id, shelf, keywords)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (name, brand, category, variants_json, price, quantity, aisle_id, shelf, keywords)
    )
    product_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return product_id


def update_product(product_id, name, brand, category, variants, aisle_id, shelf, keywords, price=0.0, quantity=""):
    """Update an existing product."""
    conn = get_connection()
    variants_json = json.dumps(variants) if isinstance(variants, list) else variants
    conn.execute(
        """UPDATE products SET name=?, brand=?, category=?, variants=?,
           price=?, quantity=?, aisle_id=?, shelf=?, keywords=? WHERE id=?""",
        (name, brand, category, variants_json, price, quantity, aisle_id, shelf, keywords, product_id)
    )
    conn.commit()
    conn.close()


def delete_product(product_id):
    """Delete a product by ID."""
    conn = get_connection()
    conn.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()


def get_all_products():
    """Get all products with their aisle information."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.*, a.name as aisle_name, a.section, a.grid_x, a.grid_y
        FROM products p
        LEFT JOIN aisles a ON p.aisle_id = a.id
        ORDER BY p.category, p.name
    """).fetchall()
    conn.close()
    products = []
    for row in rows:
        p = dict(row)
        try:
            p["variants"] = json.loads(p["variants"])
        except (json.JSONDecodeError, TypeError):
            p["variants"] = []
        products.append(p)
    return products


def get_product_by_id(product_id):
    """Get a single product by ID."""
    conn = get_connection()
    row = conn.execute("""
        SELECT p.*, a.name as aisle_name, a.section, a.grid_x, a.grid_y
        FROM products p
        LEFT JOIN aisles a ON p.aisle_id = a.id
        WHERE p.id = ?
    """, (product_id,)).fetchone()
    conn.close()
    if row:
        p = dict(row)
        try:
            p["variants"] = json.loads(p["variants"])
        except (json.JSONDecodeError, TypeError):
            p["variants"] = []
        return p
    return None


def search_products_by_text(query):
    """Basic SQL LIKE search — used as a fallback. Fuzzy search is in search.py."""
    conn = get_connection()
    pattern = f"%{query}%"
    rows = conn.execute("""
        SELECT p.*, a.name as aisle_name, a.section, a.grid_x, a.grid_y
        FROM products p
        LEFT JOIN aisles a ON p.aisle_id = a.id
        WHERE p.name LIKE ? OR p.brand LIKE ? OR p.category LIKE ? OR p.keywords LIKE ?
        ORDER BY p.name
    """, (pattern, pattern, pattern, pattern)).fetchall()
    conn.close()
    products = []
    for row in rows:
        p = dict(row)
        try:
            p["variants"] = json.loads(p["variants"])
        except (json.JSONDecodeError, TypeError):
            p["variants"] = []
        products.append(p)
    return products


def get_product_count():
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) as count FROM products").fetchone()
    conn.close()
    return row["count"]


def get_aisle_count():
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) as count FROM aisles").fetchone()
    conn.close()
    return row["count"]


def get_category_list():
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT category FROM products WHERE category != '' ORDER BY category").fetchall()
    conn.close()
    return [row["category"] for row in rows]


# ── Seed Sample Data ──────────────────────────────────────────────────

def seed_sample_data():
    """Load sample data from sample_data.json if database is empty."""
    if get_product_count() > 0:
        return  # Already has data

    sample_path = os.path.join(DB_DIR, "sample_data.json")
    if not os.path.exists(sample_path):
        return

    with open(sample_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Seed aisles first
    aisle_map = {}
    for aisle in data.get("aisles", []):
        aisle_id = add_aisle(
            aisle["name"], aisle.get("section", ""),
            aisle["grid_x"], aisle["grid_y"]
        )
        aisle_map[aisle["name"]] = aisle_id

    # Seed products
    for product in data.get("products", []):
        aisle_id = aisle_map.get(product.get("aisle", ""), None)
        add_product(
            name=product["name"],
            brand=product.get("brand", ""),
            category=product.get("category", ""),
            variants=product.get("variants", []),
            aisle_id=aisle_id,
            shelf=product.get("shelf", 1),
            keywords=product.get("keywords", ""),
            price=product.get("price", 0.0),
            quantity=product.get("quantity", "")
        )


# Initialize on import
init_db()
