import secrets
from datetime import datetime
import smtplib
from email.message import EmailMessage


# Email
def send_email(body, symbol):

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        # Create a message
        msg = EmailMessage()
        msg['Subject'] = f"Bot info - {symbol}"
        msg['From'] = secrets.user
        msg['To'] = secrets.user
        msg.set_content(body)



        smtp.login(secrets.user, secrets.password)
        smtp.send_message(msg)






