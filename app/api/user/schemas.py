from marshmallow import Schema, fields, validate


class DaoCreateUserSchema(Schema):
    username = fields.Str(
        required=True
    )
    email = fields.Str(
        required=True,
        validate=validate.Email(error='Not a valid email address')
    )
    password = fields.Str(
        required=True,
        validate=[validate.Length(min=8, max=200)]
    )
    role = fields.Str(
        required=True
    )


class DaoRegisterUserSchema(Schema):
    username = fields.Str(
        required=True
    )
    email = fields.Str(
        required=True,
        validate=validate.Email(error='Not a valid email address')
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
