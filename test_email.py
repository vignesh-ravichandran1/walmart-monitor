import os
import smtplib
from email.mime.text import MIMEText

smtp_server = os.environ['SMTP_SERVER']
smtp_port = int(os.environ['SMTP_PORT'])
from_email = os.environ['FROM_EMAIL']
to_email = os.environ['TO_EMAIL']
password = os.environ['EMAIL_PASSWORD']

msg = MIMEText("This is a test email from your GitHub Actions workflow.")
msg['Subject'] = "Test Email Connectivity"
msg['From'] = from_email
msg['To'] = to_email

try:
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(from_email, password)
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()
    print("Test email sent successfully!")
except Exception as e:
    print(f"Failed to send test email: {e}") 