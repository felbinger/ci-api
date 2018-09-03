from marshmallow import Schema, fields


class DaoCreateCategorySchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(required=True)


class DaoUpdateCategorySchema(Schema):
    description = fields.Str(required=True)
