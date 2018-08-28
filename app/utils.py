import smtplib


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
        message = f"""From: {sender}
To: {receivers[0]}
Subject: {subject}

{message}
"""
        try:
            self.conn.sendmail(sender, receivers, message)
        except smtplib.SMTPException as e:
            print(e)

    def exit(self):
        self.conn.quit()
