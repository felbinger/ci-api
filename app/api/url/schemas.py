from marshmallow import Schema, fields, validate
from ..schemas import validate_spaces


class DaoCreateCategorySchema(Schema):
    description = fields.Str(
        required=True,
        validate=[validate.Length(min=1, max=80)]
    )
    url = fields.Url(required=True)
    challenge = fields.Integer(
        required=True
    )


class DaoUpdateCategorySchema(Schema):
    description = fields.Str(
        validate=[validate.Length(min=1, max=80)]
    )
    url = fields.Url()
    challenge = fields.Integer()
