import flask
from flask import Flask, request
from .models import User
from .errors import get_response_body
from decimal import Decimal
from botocore.exceptions import ClientError
from .queries import Queries
from .serializers import parse_user

registered_users = 0
app = Flask(__name__)
connector = Queries()


@app.route("/", methods=["GET", "POST"])
def index():

    return flask.jsonify(
        ["Welcome to GBM API code challenge"]
    )


@app.route("/accounts", methods=["GET", "POST"])
def register_user():

    try:
        _cash = request.form["cash"]
        last_id = connector.get_last_user()
        new_user = User(
            cash=_cash,
            id=last_id + 1
        )
        connector.insert_item(new_user)
        return flask.jsonify(
            get_response_body(
                code=200,
                data=parse_user(new_user.__dict__),
                message=""
            ))
    except ClientError:
        return
