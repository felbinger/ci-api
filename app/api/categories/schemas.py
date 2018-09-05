from marshmallow import Schema, fields, validate


class DaoCreateCategorySchema(Schema):
    name = fields.Str(
        required=True,
        validate=[validate.Length(min=1, max=50), validate_spaces]
    )
    description = fields.Str(
        required=True,
        validate=[validate.Length(min=1, max=150)]
    )


class DaoUpdateCategorySchema(Schema):
    description = fields.Str(
        required=True,
        validate=[validate.Length(min=1, max=150)]
    )
