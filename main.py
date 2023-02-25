import os

from imap_tools import MailBox, A
from dotenv import load_dotenv
from smtplib import SMTP_SSL as SMTP
from email.mime.text import MIMEText


def fetch_mails():
    isDebug = os.getenv('DEBUG') == 'true'

    server = os.getenv('IMAP_SERVER')
    mail_address = os.getenv('IMAP_MAIL')
    password = os.getenv('IMAP_PASSWORD')

    with MailBox(server).login(mail_address, password) as mailbox:
        criteria = A(seen=isDebug)

        return list(mailbox.fetch(criteria, mark_seen=True))


def forward_mail(mail):
    server = os.getenv('SMTP_SERVER')
    mail_address = os.getenv('SMTP_MAIL')
    password = os.getenv('SMTP_PASSWORD')

    forward_to = os.getenv('FORWARD_TO')

    message = MIMEText(mail.html, 'html')
    message['Subject'] = mail.subject
    message['Reply-To'] = mail.from_
    message['From'] = mail_address

    for attachment in mail.attachments:
        message.attach(attachment)

    connection = SMTP(server)
    connection.set_debuglevel(False)
    connection.login(mail_address, password)

    try:
        connection.sendmail(mail_address, forward_to, message.as_string())
    finally:
        connection.quit()


if __name__ == '__main__':
    print('Loading environment...')
    load_dotenv()

    print('Fetching mails...')
    mails = fetch_mails()

    for received_mail in mails:
        print('Forwarding mail ' + received_mail.subject + '...')
        forward_mail(received_mail)
