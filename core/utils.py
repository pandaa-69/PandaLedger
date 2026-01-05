import threading
import logging
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)

class EmailThread(threading.Thread):
    """
    A thread subclass to send emails asynchronously.
    
    This ensures that the main request-response cycle is not blocked 
    by the potentially slow SMTP network operation.
    """
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        """
        Executes the email sending process in a separate thread.
        """
        try:
            self.email.send()
            logger.info(f"✅ Email sent successfully to: {self.email.to}")
        except Exception as e:
            logger.error(f"❌ Email sending failed: {e}", exc_info=True)

def send_email_async(data):
    """
    Utility function to send emails without blocking the main application thread.

    Args:
        data (dict): A dictionary containing email details.
            - subject (str): The subject line of the email.
            - body (str): The main content of the email.
            - to (str or list): The recipient email address(es).

    Usage:
        send_email_async({
            'subject': 'Welcome!',
            'body': 'Thank you for signing up.',
            'to': 'user@example.com'
        })
    """
    # Ensure receiver is a list, even if a single string is passed
    recipient_list = [data['to']] if isinstance(data['to'], str) else data['to']

    email = EmailMessage(
        subject=data['subject'],
        body=data['body'],
        to=recipient_list
    )
    
    # Start the daemon thread to send email
    EmailThread(email).start()
