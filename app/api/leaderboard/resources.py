from flask.views import MethodView
from sqlalchemy import func

from app.db import db
from ..schemas import ResultSchema
from ..authentication import require_token
from ..user import User
from ..challenge import Challenge


class LeaderboardResource(MethodView):
    """
    curl -H "Access-Token: $token" -X GET localhost:5000/api/leaderboard
    curl -H "Access-Token: $token" -X GET localhost:5000/api/leaderboard/me
    """

    @require_token
    def get(self, name, user, **_):
        if name == 'me':
            point_list = [{"points": sum(
                               [solve.challenge.points for solve in user.solves if
                                not solve.challenge.solution_date or solve.challenge.solution_date > solve.timestamp]),
                           "user": user} for user in User.query.all()]
            ranks = sorted(point_list, key=lambda p: p["points"], reverse=True)
            rank = next(iter([i + 1 for i, rank in enumerate(ranks) if rank["user"] == user]))

            return ResultSchema(
                data=rank
            ).jsonify()
        else:
            point_list = [{"points": sum(
                               [solve.challenge.points for solve in user.solves if
                                not solve.challenge.solution_date or solve.challenge.solution_date > solve.timestamp]),
                           "user": user} for user in User.query.all()]
            top = sorted(point_list, key=lambda p: p["points"], reverse=True)[:10]

            for i, entry in enumerate(top):
                top[i] = {
                    "username": entry["user"].username,
                    "points": entry["points"],
                    "rank": i + 1
                }

            return ResultSchema(
                data=top
            ).jsonify()
