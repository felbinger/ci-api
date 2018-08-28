from marshmallow import Schema, fields, validate


class DaoSolveChallengeSchema(Schema):
    flag = fields.Str(required=True)
