import os
import requests
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
from datetime import datetime
import logging

class WalmartMonitor:
    def __init__(self, product_url, email_config=None):
        self.product_url = product_url
        self.email_config = email_config
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('walmart_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def check_availability(self):
        try:
            response = requests.get(self.product_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text().lower()
            add_to_cart_selectors = [
                'button[data-automation-id="add-to-cart-button"]',
                'button[data-testid="add-to-cart-button"]',
                'button[aria-label*="add to cart"]',
                'button:contains("Add to cart")',
                '[data-automation-id="atc-button"]'
            ]
            add_to_cart_found = False
            for selector in add_to_cart_selectors:
                button = soup.select_one(selector)
                if button and not button.get('disabled') and 'disabled' not in button.get('class', []):
                    add_to_cart_found = True
                    break
            out_of_stock_indicators = [
                'out of stock',
                'sold out',
                'not available',
                'temporarily unavailable',
                'currently unavailable',
                'indisponible',
                'en rupture de stock'
            ]
            is_out_of_stock = any(indicator in page_text for indicator in out_of_stock_indicators)
            price_elements = soup.find_all(['span', 'div'], class_=lambda x: x and 'price' in x.lower())
            has_price = len(price_elements) > 0
            delivery_indicators = [
                'free shipping',
                'pickup',
                'delivery available',
                'livraison gratuite'
            ]
            has_delivery_options = any(indicator in page_text for indicator in delivery_indicators)
            if add_to_cart_found and not is_out_of_stock:
                return True, "✅ Product is AVAILABLE - Add to Cart button found and no out-of-stock indicators"
            elif is_out_of_stock:
                return False, "❌ Product is OUT OF STOCK - Out of stock text found on page"
            elif has_price and has_delivery_options and not is_out_of_stock:
                return True, "✅ Product appears AVAILABLE - Price and delivery options shown"
            elif 'add to cart' in page_text and not is_out_of_stock:
                return True, "✅ Product appears AVAILABLE - Add to cart text found"
            else:
                return False, "❌ Product appears UNAVAILABLE - No clear availability indicators found"
        except requests.RequestException as e:
            self.logger.error(f"Network error fetching product page: {e}")
            return None, f"❗ Error checking availability: {e}"
        except Exception as e:
            self.logger.error(f"Unexpected error parsing page: {e}")
            return None, f"❗ Error parsing page: {e}"

    def send_notification(self, subject, message):
        if not self.email_config:
            print(f"NOTIFICATION: {subject}")
            print(message)
            return
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = self.email_config['to_email']
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['from_email'], self.email_config['password'])
            text = msg.as_string()
            server.sendmail(self.email_config['from_email'], self.email_config['to_email'], text)
            server.quit()
            self.logger.info("Email notification sent successfully")
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")

    def monitor_once(self):
        is_available, message = self.check_availability()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "AVAILABLE" if is_available else "UNAVAILABLE"
        self.logger.info(f"[{timestamp}] Product is {status}: {message}")
        subject = f"Walmart Product Alert - {status}"
        notification_message = f"""
Product Status Update:

URL: {self.product_url}
Status: {status}
Details: {message}
Time: {timestamp}

This is an automated notification from your Walmart product monitor.
        """
        self.send_notification(subject, notification_message)

def get_config_from_env():
    product_url = os.environ['PRODUCT_URL']
    email_config = {
        'smtp_server': os.environ['SMTP_SERVER'],
        'smtp_port': int(os.environ['SMTP_PORT']),
        'from_email': os.environ['FROM_EMAIL'],
        'password': os.environ['EMAIL_PASSWORD'],
        'to_email': os.environ['TO_EMAIL']
    }
    return product_url, email_config

if __name__ == "__main__":
    product_url, email_config = get_config_from_env()
    monitor = WalmartMonitor(product_url, email_config)
    monitor.monitor_once() 