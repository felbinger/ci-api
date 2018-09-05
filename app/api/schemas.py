from flask import jsonify
from marshmallow import ValidationError


def validate_spaces(text):
    if " " in text:
        raise ValidationError("Text should'nt contain any space")


class ResultErrorSchema:
    __slots__ = ['message', 'errors', 'data', 'status_code']

    def __init__(self, message, errors=None, status_code=400):
        self.message = message
        self.errors = errors or []
        self.status_code = status_code

    def jsonify(self):
        return jsonify({
            'message': self.message,
            'errors': self.errors,
            'statusCode': self.status_code
        }), self.status_code


class ResultSchema:
    __slots__ = ['data', 'status_code']

    def __init__(self, data=None, status_code=200):
        self.data = data
        self.status_code = status_code

    def jsonify(self):
        return jsonify({
            'data': self.data,
            'statusCode': self.status_code
        }), self.status_code
