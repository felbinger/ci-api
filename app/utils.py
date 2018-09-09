import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import COMMASPACE


class SMTPMail:
    def __init__(self, host, port, username, password):
        self.conn = smtplib.SMTP(host, port)
        self.conn.ehlo()
        self.conn.starttls()
        try:
            self.conn.login(username, password)
        except smtplib.SMTPAuthenticationError as e:
            print(e)

    def sendmail(self, subject, message, receivers=[], sender='no-reply@the-morpheus.de'):
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = COMMASPACE.join(receivers)
        msg['Subject'] = subject
        msg.attach(MIMEText(message, _charset='utf-8'))

        try:
            self.conn.sendmail(sender, receivers, msg.as_string())
        except smtplib.SMTPException as e:
            print(e)

    def exit(self):
        self.conn.quit()
