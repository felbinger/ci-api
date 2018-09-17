from marshmallow import Schema, fields, validate

from ..schemas import validate_spaces


class DaoCreateChallengeSchema(Schema):
    name = fields.Str(
        required=True,
        validate=[validate.Length(min=1, max=120)]
    )
    description = fields.Str()
    flag = fields.Str(
        required=True,
        validate=[validate.Length(min=1, max=800)]
    )
    points = fields.Integer(
        required=True
    )
    category = fields.Str(
        required=True,
        validate=[validate.Length(min=1, max=50), validate_spaces]
    )
    yt_challenge_id = fields.Str(
        load_from='ytChallengeId',
        validate=[validate.Length(min=0, max=20)]
    )
    yt_solution_id = fields.Str(
        load_from='ytSolutionId',
        validate=[validate.Length(min=0, max=20)]
    )
    publication = fields.DateTime(
        required=True  # TODO how does this work @Daniel
    )


class DaoUpdateChallengeSchema(Schema):
    description = fields.Str(
        validate=[validate.Length(min=0, max=800)]
    )
    category = fields.Str(
        validate=[validate.Length(min=1, max=50), validate_spaces]
    )
    points = fields.Integer()
    yt_challenge_id = fields.Str(
        load_from='ytChallengeId',
        validate=[validate.Length(min=0, max=20)]
    )
    yt_solution_id = fields.Str(
        load_from='ytSolutionId',
        validate=[validate.Length(min=0, max=20)]
    )
