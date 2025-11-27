"""
Background Worker - Production Price Checker
This runs independently from the Flask app to check prices 24/7

File: background_worker.py
"""

import time
import sys
from datetime import datetime
from database.db import init_db, get_all_products, update_product_price
from services.price_scraper import fetch_price
from services.email_service import send_price_alert
from config import Config

def check_prices_cycle():
    """Single cycle of checking all products"""
    print(f"\n{'='*70}")
    print(f"🔄 Price Check Cycle Started - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    try:
        products = get_all_products()
        
        if not products:
            print("⚠️  No products in database to check")
            return
        
        print(f"📊 Found {len(products)} product(s) to check\n")
        
        checked = 0
        changed = 0
        errors = 0
        
        for product in products:
            # Handle both old (8 columns) and new (9 columns) database formats
            if len(product) == 9:
                product_id, name, url, email, css_selector, old_price, _, use_selenium, _ = product
            else:
                product_id, name, url, email, css_selector, old_price, _, _ = product
                use_selenium = False
            
            print(f"{'─'*70}")
            print(f"🏷️  {name}")
            print(f"   Current: R{old_price if old_price else 'N/A'}")
            print(f"   Checking...")
            
            try:
                new_price = fetch_price(url, css_selector, force_selenium=use_selenium)
                
                if new_price:
                    update_product_price(product_id, new_price)
                    checked += 1
                    
                    if old_price and old_price != new_price:
                        change_amount = new_price - old_price
                        change_percent = (change_amount / old_price * 100)
                        
                        print(f"   🔔 PRICE CHANGED!")
                        print(f"   Old: R{old_price:.2f}")
                        print(f"   New: R{new_price:.2f}")
                        print(f"   Change: R{change_amount:.2f} ({change_percent:+.1f}%)")
                        print(f"   📧 Sending email to {email}...")
                        
                        send_price_alert(email, name, old_price, new_price, url)
                        changed += 1
                        print(f"   ✅ Email sent!")
                    else:
                        print(f"   ✓ Price unchanged: R{new_price:.2f}")
                else:
                    print(f"   ❌ Could not detect price")
                    errors += 1
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                errors += 1
        
        # Summary
        print(f"\n{'='*70}")
        print(f"📊 Cycle Summary:")
        print(f"   ✅ Checked: {checked}/{len(products)}")
        print(f"   🔔 Changed: {changed}")
        print(f"   ❌ Errors: {errors}")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"❌ Critical error in check cycle: {e}")
        import traceback
        traceback.print_exc()

def run_worker():
    """Main worker loop - runs forever"""
    print("\n" + "="*70)
    print("🚀 Price Tracker Background Worker Started")
    print("="*70)
    print(f"⏰ Check Interval: {Config.CHECK_INTERVAL} seconds ({Config.CHECK_INTERVAL/3600:.1f} hours)")
    print(f"📧 Email: {Config.GMAIL_USER}")
    print(f"🗄️  Database: {Config.DATABASE_PATH}")
    print("="*70 + "\n")
    
    # Initialize database
    try:
        init_db()
        print("✅ Database initialized\n")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)
    
    # Main loop
    cycle_count = 0
    
    while True:
        try:
            cycle_count += 1
            print(f"\n🔢 Cycle #{cycle_count}")
            
            check_prices_cycle()
            
            # Wait for next cycle
            next_check = datetime.now().timestamp() + Config.CHECK_INTERVAL
            next_check_time = datetime.fromtimestamp(next_check).strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"⏰ Sleeping for {Config.CHECK_INTERVAL} seconds")
            print(f"⏰ Next check at: {next_check_time}")
            print(f"💤 Zzz...\n")
            
            time.sleep(Config.CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\n👋 Worker stopped by user")
            sys.exit(0)
            
        except Exception as e:
            print(f"\n❌ Unexpected error in main loop: {e}")
            import traceback
            traceback.print_exc()
            print("\n⏰ Waiting 60 seconds before retry...")
            time.sleep(60)

if __name__ == "__main__":
    try:
        run_worker()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)