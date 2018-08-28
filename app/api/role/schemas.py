from marshmallow import Schema, fields


class DaoCreateRoleSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(required=True)


class DaoUpdateRoleSchema(Schema):
    description = fields.Str(required=True)
