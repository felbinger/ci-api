from marshmallow import Schema, fields, validate


class DaoSolveChallengeSchema(Schema):
    flag = fields.Str(
        required=True,
        validate=[validate.Length(min=1, max=80)]
    )
