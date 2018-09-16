from flask.views import MethodView
from flask import request

from app.db import db
from ..schemas import ResultSchema, ResultErrorSchema
from ..authentication import require_token, require_admin
from .models import Message
from .schemas import DaoCreateMessageSchema


class MessageResource(MethodView):
    """
    curl -H "Access-Token: $token" -X GET localhost:5000/api/messages
    curl -H "Access-Token: $token" -X GET localhost:5000/api/messages/1
    """
    @require_token
    @require_admin
    def get(self, _id, **_):
        if _id is None:
            return ResultSchema(
                data=[d.jsonify() for d in Message.query.all()]
            ).jsonify()
        else:
            data = Message.query.filter_by(id=_id).first()
            if not data:
                return ResultErrorSchema(
                    message='Message does not exist!',
                    errors=['message does not exist'],
                    status_code=404
                ).jsonify()
            return ResultSchema(
                data=data.jsonify()
            ).jsonify()

    """
    curl -X POST localhost:5000/api/messages -H "Access-Token: $token" -H "Content-Type: application/json" \
    -d '{"subject": "TestSubject", "message": "This is a bug"}'
    """
    @require_token
    def post(self, user, **_):
        data = request.get_json() or {}
        schema = DaoCreateMessageSchema()
        result = schema.load(data)
        if result.errors:
            return ResultErrorSchema(
                message='Payload is invalid',
                errors=result.errors,
                status_code=400
            ).jsonify()
        data = result.data
        message = Message.query.filter(Message.subject == data['subject']).first()
        if message:
            return ResultErrorSchema(
                message='Message subject already in use!',
                errors=['Message subject already in use'],
                status_code=422
            ).jsonify()
        data['user'] = user
        msg = Message(**data)
        db.session.add(msg)
        db.session.commit()

        return ResultSchema(
            data=msg.jsonify(),
            status_code=201
        ).jsonify()

    """
    curl -X DELETE localhost:5000/api/messages/1 -H "Access-Token: $token"
    """
    @require_token
    @require_admin
    def delete(self, _id, **_):
        message = Message.query.filter_by(id=_id).first()
        db.session.delete(message)
        db.session.commit()
        return '', 204