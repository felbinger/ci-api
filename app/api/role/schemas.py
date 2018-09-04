from marshmallow import Schema, fields, validate


class DaoCreateRoleSchema(Schema):
    name = fields.Str(
        required=True,
        validate=[validate.Length(min=1, max=50)]
    )
    description = fields.Str(
        required=True,
        validate=[validate.Length(min=1, max=150)]
    )


class DaoUpdateRoleSchema(Schema):
    description = fields.Str(
        required=True,
        validate=[validate.Length(min=1, max=150)]
    )
