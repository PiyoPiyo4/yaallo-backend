import os
import sendgrid
from sendgrid.helpers.mail import Mail, From, To, Subject, Content
import random
from flask_cors import CORS, cross_origin
from python_http_client.exceptions import HTTPError
# SENDGRID_API_KEY = os.getenv("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")
# api_key = os.getenv("YOUR_API_KEY")

def generate_otp():
  otp = ''.join(random.choices('0123456789', k=4))
  return otp

@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def send_email(recipient_email, subject, content):
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    message = Mail(
        from_email=From("yaallo.noreply@gmail.com", "yaallO"),
        to_emails=To(recipient_email),
        subject=Subject(subject),
        plain_text_content=Content("text/plain", content),
        html_content=Content("text/html", content)
    )
    try:
        response = sg.client.mail.send.post(request_body=message.get())
    except HTTPError as e:
        print(e.to_dict)
    if response.status_code == 202:
        print("Email sent successfully!")
        return '1'
    else:
        print(f"Error sending email: {response.status_code}")
        return '0'

