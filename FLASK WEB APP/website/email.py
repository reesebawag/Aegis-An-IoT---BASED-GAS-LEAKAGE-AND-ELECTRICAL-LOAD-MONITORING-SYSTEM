
from flask_mail import Message

from . import mail

def send_email( subject, body, recipient_email):
   
    msg = Message(subject,recipients=[recipient_email], sender= 'noreply@demo.com' )
    msg.body = body
    mail.send(msg)
