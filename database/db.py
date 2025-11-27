"""
Enhanced Database Functions with Selenium support flag
File: database/db.py
"""

import sqlite3
from datetime import datetime

DATABASE_PATH = '/data/price_tracker.db'


def init_db():
    """Initialize the database with the products table"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # Check if table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
    table_exists = c.fetchone()
    
    if not table_exists:
        # Create new table with use_selenium column
        c.execute('''CREATE TABLE IF NOT EXISTS products
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      url TEXT NOT NULL,
                      email TEXT NOT NULL,
                      css_selector TEXT,
                      current_price REAL,
                      last_checked TIMESTAMP,
                      use_selenium INTEGER DEFAULT 0,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    else:
        # Add use_selenium column if it doesn't exist
        try:
            c.execute("ALTER TABLE products ADD COLUMN use_selenium INTEGER DEFAULT 0")
            print("✓ Database upgraded: added use_selenium column")
        except sqlite3.OperationalError:
            # Column already exists
            pass
    
    conn.commit()
    conn.close()

def add_product(name, url, email, css_selector, current_price, use_selenium=False):
    """Add a new product to track"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("""INSERT INTO products (name, url, email, css_selector, current_price, last_checked, use_selenium)
                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (name, url, email, css_selector, current_price, datetime.now(), 1 if use_selenium else 0))
    conn.commit()
    conn.close()

def get_all_products():
    """Get all tracked products"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM products ORDER BY created_at DESC")
    products = c.fetchall()
    conn.close()
    return products

def update_product_price(product_id, new_price):
    """Update a product's price and last checked time"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("UPDATE products SET current_price = ?, last_checked = ? WHERE id = ?",
             (new_price, datetime.now(), product_id))
    conn.commit()
    conn.close()

def delete_product(product_id):
    """Delete a product from tracking"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()