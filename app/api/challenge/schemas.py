from marshmallow import Schema, fields, validate


class DaoCreateChallengeSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    flag = fields.Str(required=True)
    category = fields.Str(required=True)


class DaoUpdateChallengeSchema(Schema):
    description = fields.Str(validate=[validate.Length(min=1, max=512)])
    yt_challenge_id = fields.Str(validate=[validate.Length(min=1, max=10)])
    yt_solution_id = fields.Str(validate=[validate.Length(min=1, max=10)])
