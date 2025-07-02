# Walmart Monitor

Monitors a Walmart product page for availability and sends an email notification if the status changes.

## Usage

1. Set the following repository secrets in GitHub:
   - `PRODUCT_URL`
   - `SMTP_SERVER`
   - `SMTP_PORT`
   - `FROM_EMAIL`
   - `EMAIL_PASSWORD`
   - `TO_EMAIL`

2. The monitor will run every 30 minutes via GitHub Actions and send an email if the product is available or unavailable.

## Local Testing

Install dependencies:
```
pip install -r requirements.txt
```
Set environment variables and run:
```
export PRODUCT_URL="https://www.walmart.ca/en/ip/seort/6000207867431"
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export FROM_EMAIL="your_email@gmail.com"
export EMAIL_PASSWORD="your_app_password"
export TO_EMAIL="recipient_email@gmail.com"
python walmart_monitor.py
```