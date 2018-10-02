from flask.views import MethodView

from app.db import db
from ..schemas import ResultSchema
from ..authentication import require_token
from ..user import User


class LeaderboardResource(MethodView):
    """
    curl -H "Access-Token: $token" -X GET localhost:5000/api/leaderboard
    curl -H "Access-Token: $token" -X GET localhost:5000/api/leaderboard/me
    """
    @require_token
    def get(self, name, user, **_):
        if name == 'me':
            # TODO rewrite to sqlalchemy - tests wont work
            rank = list(db.engine.execute(f"""
                SELECT COUNT(*)
                FROM (
                    SELECT SUM(challenge.points) AS points FROM solve
                    JOIN user on user.id = solve.user
                    JOIN challenge on challenge.id = solve.challenge
                    GROUP BY user.id
                ) re
                WHERE re.points > {user.get_points()}
            """))[0][0]

            return ResultSchema(
                data=rank + 1
            ).jsonify()
        else:
            data = []
            # TODO rewrite to sqlalchemy - tests wont work
            top = list(db.engine.execute("""
                SELECT *
                FROM (
                    SELECT user.id as id, SUM(challenge.points) AS points FROM solve
                    JOIN user on user.id = solve.user
                    JOIN challenge on challenge.id = solve.challenge
                    GROUP BY user.id
                ) a
                ORDER BY a.points DESC
            """))

            for i, user_data in enumerate(top):
                # todo rewrite
                if i == 10:
                    break
                user = User.query.filter_by(id=user_data[0]).first()
                data.append({
                    "username": user.username,
                    "points": int(user_data[1]),
                    "rank": i + 1
                })

            return ResultSchema(
                data=data
            ).jsonify()
