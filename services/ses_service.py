import boto3

from decouple import config
from botocore.exceptions import ClientError
from werkzeug.exceptions import InternalServerError


class SESEmail:

    def __init__(self):
        self.access_key = config("AWS_ACCESS_KEY")
        self.secret_key = config("AWS_SECRET_KEY")
        self.region = config("AWS_REGION")
        self.ses = boto3.client(
            "ses",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
        )

    def send_email(self, recipient, subject, content):

        sender = config("SES_EMAIL_SENDER")
        try:
            response = self.ses.send_email(
                Source=sender,
                Destination={"ToAddresses": [recipient]},
                Message={
                    "Subject": {"Data": subject, "Charset": "UTF-8"},
                    "Body": {"Text": {"Data": content, "Charset": "UTF-8"}},
                },
            )
        except ClientError as ex:
            raise InternalServerError(f"Failed to send email: {ex}")


ses_email = SESEmail()
