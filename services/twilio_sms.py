from decouple import config
from twilio.rest import Client


class TwilioSMS:

    def __init__(self):
        self.account_sid = config("TWILIO_SID")
        self.auth_token = config("TWILIO_TOKEN")
        self.twilio_number = config("TWILIO_NUMBER")

    def send_notification(self, recipient_number: str, message: str):
        client = Client(self.account_sid, self.auth_token)

        message = client.messages.create(
            body=message, from_=self.twilio_number, to=recipient_number
        )


twilio_notify = TwilioSMS()
