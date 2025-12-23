import threading
from django.core.mail import EmailMessage
import sys

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        try:
            self.email.send()
            print("✅ EMAIL SENT SUCCESSFULLY", flush=True) # 👈 Add flush=True
        except Exception as e:
            # This forces the error to show up in Render logs immediately
            print(f"❌ EMAIL FAILED: {str(e)}", file=sys.stderr, flush=True)

def send_email_async(data):
    """
    data = {
        'subject': 'Your Subject',
        'body': 'Your Message',
        'to': 'user@example.com'
    }
    """
    email = EmailMessage(
        subject=data['subject'],
        body=data['body'],
        to=[data['to']]
    )
    EmailThread(email).start()