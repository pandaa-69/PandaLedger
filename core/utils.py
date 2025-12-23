import threading
from django.core.mail import EmailMessage

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        try:
            self.email.send()
            print("✅ Email sent successfully (Background)")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")

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