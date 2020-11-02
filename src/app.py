import flask
import time
from flask import Flask, request
from .models import User, Transaction
from .errors import get_response_body
from decimal import Decimal
from botocore.exceptions import ClientError
from .custom_exceptions import (
    NoStockError,
    TimestampError,
    NegativeValuesError,
    ServiceNotAvailable,
    NotEnoughBalanceError,
    InvalidOperationError,
    SameTransactionException,)
from datetime import datetime
from .queries import Queries, RedisDB
from .serializers import parse_user

registered_users = 0
app = Flask(__name__)
connector = Queries()
cache = RedisDB()


@app.route("/", methods=["GET", "POST"])
def index():

    return flask.jsonify(
        ["Welcome to GBM API code challenge"]
    )


@app.route("/accounts", methods=["POST"])
def register_user():

    try:
        _cash = request.form["cash"]
        last_id = connector.get_last_user()
        _id = last_id + 1
        new_user = User(
            cash=_cash,
            id=_id
        )
        connector.insert_item(new_user)

        new_transaction = Transaction(
            id=_id,
            operation="account_created",
            issuer_name="",
            share_price=Decimal("0"),
            total_shares=Decimal("0"),
            user_shares=Decimal(0),
            change_cash=Decimal("0"),
            change_shares=Decimal("0"),
            time=str(int(time.time())),
            user_balance=_cash,
        )
        connector.insert_item(new_transaction)
        return flask.jsonify(
            get_response_body(
                code=200,
                data=parse_user(new_user.__dict__),
                message=""
            ))

    # Something went wrong when calling DynamoDB
    except ClientError as e:
        return flask.jsonify(
            get_response_body(
                code=400,
                data=dict(),
                message=e
            ))
