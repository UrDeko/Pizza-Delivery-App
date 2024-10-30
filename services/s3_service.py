import boto3

from botocore.exceptions import ClientError
from decouple import config
from werkzeug.exceptions import InternalServerError


class S3Service:

    def __init__(self):
        self.access_key = config("AWS_ACCESS_KEY")
        self.secret_key = config("AWS_SECRET_KEY")
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        )
        self.bucket = config("AWS_BUCKET")

    def upload_photo(self, path, key, extension):

        try:
            self.s3.upload_file(
                path, self.bucket, key, ExtraArgs={"ContentType": f"image/{extension}"}
            )
            return f"https://{config("AWS_BUCKET")}.s3.{config("AWS_REGION")}.amazonaws.com/{key}"
        except ClientError as ex:
            raise InternalServerError(f"S3 is not available at the moment {str(ex)}")


s3_store = S3Service()
