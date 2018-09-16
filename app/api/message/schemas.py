from marshmallow import Schema, fields, validate


class DaoCreateMessageSchema(Schema):
    message = fields.Str(
        required=True,
        validate=[validate.Length(min=1, max=1000)]
    )
    subject = fields.Str(
        required=True,
        validate=[validate.Length(min=1, max=80)]
    )
