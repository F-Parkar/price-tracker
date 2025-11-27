"""
Enhanced Flask App with Selenium Support
File: app.py
"""

import threading
import time
from flask import Flask, render_template, request, redirect, url_for, flash

from config import Config
from database.db import init_db, add_product, get_all_products, update_product_price, delete_product
from services.price_scraper import fetch_price
from services.email_service import send_price_alert

app = Flask(__name__)
app.config.from_object(Config)

def check_prices_background():
    """Background task to check prices periodically"""
    while True:
        time.sleep(Config.CHECK_INTERVAL)
        print("\n🔄 Starting price check cycle...")
        
        products = get_all_products()
        
        for product in products:
            # Handle both old (8 columns) and new (9 columns) database formats
            if len(product) == 9:
                product_id, name, url, email, css_selector, old_price, _, use_selenium, _ = product
            else:
                product_id, name, url, email, css_selector, old_price, _, _ = product
                use_selenium = False
            
            print(f"Checking: {name}")
            new_price = fetch_price(url, css_selector, force_selenium=use_selenium)
            
            if new_price:
                update_product_price(product_id, new_price)
                
                if old_price and old_price != new_price:
                    send_price_alert(email, name, old_price, new_price, url)
                    print(f"✓ Price changed for {name}: R{old_price} -> R{new_price}")
                else:
                    print(f"✓ Price unchanged: R{new_price}")
            else:
                print(f"❌ Could not fetch price for {name}")
        
        print("✓ Price check cycle complete\n")

@app.route('/')
def index():
    """Main page with form to add products"""
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add():
    """Add a new product to track"""
    name = request.form.get('name')
    url = request.form.get('url')
    email = request.form.get('email')
    css_selector = request.form.get('css_selector', '').strip() or None
    use_selenium = request.form.get('use_selenium') == 'on'
    
    if not name or not url or not email:
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('index'))
    
    # Fetch initial price
    print(f"\n🔍 Detecting price for: {name}")
    current_price = fetch_price(url, css_selector, force_selenium=use_selenium)
    
    if current_price is None:
        flash('Could not detect price. Try enabling "Use JavaScript rendering" or provide a CSS selector.', 'error')
        return redirect(url_for('index'))
    
    add_product(name, url, email, css_selector, current_price, use_selenium)
    
    flash(f'✓ Product added! Current price: R{current_price:.2f}', 'success')
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """Dashboard showing all tracked products"""
    products = get_all_products()
    return render_template('dashboard.html', products=products)

@app.route('/delete/<int:product_id>')
def delete(product_id):
    """Remove a product from tracking"""
    delete_product(product_id)
    flash('Product removed from tracking.', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    init_db()
    
    # Start background price checker
    #checker_thread = threading.Thread(target=check_prices_background, daemon=True)
    #checker_thread.start()
    
    print("="*60)
    print("🏷️  Price Tracker - Enhanced Edition (React/SPA Support)")
    print("="*60)
    print("✓ Server running at: http://127.0.0.1:5000")
    print("✓ Database initialized")
    print("✓ Background price checker started")
    print("\n🚀 Features:")
    print("  • Automatic price detection")
    print("  • React/SPA support with Selenium")
    print("  • Email notifications on price changes")
    print("\n📧 Email Configuration:")
    print("  Make sure your .env file has:")
    print("  GMAIL_USER=your-email@gmail.com")
    print("  GMAIL_PASSWORD=your-app-password")
    print("\n🌐 Selenium Setup (for React apps):")
    print("  pip install selenium")
    print("  Then download ChromeDriver for your system")
    print("="*60)
    
    app.run(debug=True, use_reloader=False)