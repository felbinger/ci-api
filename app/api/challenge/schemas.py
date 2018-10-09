from marshmallow import Schema, fields, validate
import dateutil.parser
from datetime import datetime

from ..schemas import validate_spaces


class IsoDateTime(fields.Field):
    default_error_messages = {
        "invalid_datetime": "Invalid datetime format, please use ISO8607"
    }

    def _serialize(self, value, attr, obj):
        return dateutil.parser.parse(value)

    def _validate(self, value):
        try:
            if not bool(dateutil.parser.parse(value)):
                self.fail("invalid_datetime")
        except ValueError:
            self.fail("invalid_datetime")


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
    publication = IsoDateTime(
        default=datetime.now()
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
