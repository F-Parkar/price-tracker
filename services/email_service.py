
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

def send_price_alert(to_email, product_name, old_price, new_price, product_url=None):
    """Send email notification about price change"""
    gmail_user = Config.GMAIL_USER
    gmail_password = Config.GMAIL_PASSWORD
    
    if not gmail_user or not gmail_password or gmail_user == 'your-email@gmail.com':
        print(f"Email not configured. Would send: {product_name} price changed from R{old_price} to R{new_price}")
        return
    
    # Calculate price change
    price_diff = new_price - old_price
    percent_change = (price_diff / old_price * 100) if old_price > 0 else 0
    
    subject = f"🔔 Price Alert: {product_name}"
    
    # Build email body with URL
    body = f"""
Hello!

Great news! The price for {product_name} has changed:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Previous Price: R{old_price:.2f}
New Price: R{new_price:.2f}
Change: R{price_diff:.2f} ({percent_change:+.1f}%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{'🎉 Price dropped! This might be a great time to buy!' if price_diff < 0 else '📈 Price increased.'}
"""
    
    # Add product URL if provided
    if product_url:
        body += f"""

🔗 View Product:
{product_url}

Click the link above to check it out!
"""
    
    body += """

Happy shopping!
- Your Price Tracker
    """
    
    try:
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.send_message(msg)
        server.quit()
        print(f"✓ Email sent to {to_email}")
    except Exception as e:
        print(f"✗ Failed to send email: {e}")