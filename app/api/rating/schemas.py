from marshmallow import Schema, fields


class DaoRateSchema(Schema):
    thumb_up = fields.Boolean(
        load_from='thumbUp',
        required=True
    )

