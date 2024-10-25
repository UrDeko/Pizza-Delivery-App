from marshmallow import fields, Schema, validates, validates_schema, ValidationError
from marshmallow.validate import OneOf
from password_strength import PasswordPolicy


class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class UserRegisterSchema(UserLoginSchema):
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    phone = fields.String(required=True)

    @validates("password")
    def validate_password(self, value: str):

        if len(value.strip()) < 8 and len(value.strip()) > 12:
            ValidationError(
                "Password length should be between 8 and 12 characters long"
            )

        policy = PasswordPolicy.from_names(
            uppercase=2, numbers=2, special=2, nonletters=2
        )

        result = policy.test(value)

        if result:
            raise ValidationError(
                "Invalid password. Required: uppercase - 2, numbers - 2, special - 2, nonletters - 2"
            )

    @validates("first_name")
    def validate_first_name(self, value: str):

        if len(value.strip()) < 2:
            raise ValidationError("First name should consist of 2 or more characters")

    @validates("last_name")
    def validate_last_name(self, value: str):

        if len(value.strip()) < 2:
            raise ValidationError("Last name should consist of 2 or more characters")

    @validates("phone")
    def validate_phone(self, value: str):

        if (
            not value.startswith("+")
            or not value[1:].isnumeric()
            or (len(value.strip()) < 10 or len(value.strip()) > 17)
        ):
            raise ValidationError("Invalid phone number")


class UserCreateRequestSchema(UserRegisterSchema):
    role = fields.String(required=True, validate=OneOf(["admin", "chef", "deliver"]))


class PasswordChangeSchema(Schema):
    old_password = fields.String(required=True)
    new_password = fields.String(required=True)

    @validates_schema
    def validate_passwords(self, data, **kwargs):
        if data["old_password"] == data["new_password"]:
            raise ValidationError(
                "New password cannot be the same as the old password",
                field_names=["new_password"],
            )
