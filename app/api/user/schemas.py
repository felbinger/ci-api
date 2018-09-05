from marshmallow import Schema, fields, validate
from ..schemas import validate_spaces


class DaoCreateUserSchema(Schema):
    username = fields.Str(
        required=True,
        validate=[validate.Length(min=1, max=80), validate_spaces]
    )
    email = fields.Str(
        required=True,
        validate=[validate.Email(error='Not a valid email address'), validate.Length(min=8, max=200), validate_spaces]
    )
    password = fields.Str(
        required=True,
        validate=[validate.Length(min=8, max=200)]
    )
    role = fields.Str(
        required=True,
        validate=[validate.Length(min=1, max=50)]
    )


class DaoRegisterUserSchema(Schema):
    username = fields.Str(
        required=True,
        validate=[validate.Length(min=1, max=80), validate_spaces]
    )
    email = fields.Str(
        required=True,
        validate=[validate.Email(error='Not a valid email address'), validate.Length(min=8, max=200), validate_spaces]
    )
    password = fields.Str(
        required=True,
        validate=[validate.Length(min=8, max=200)]
    )


class DaoUpdateUserSchema(Schema):
    username = fields.Str()
    email = fields.Str()
    password = fields.Str(validate=[validate.Length(min=8, max=200)])
    role = fields.Str()
