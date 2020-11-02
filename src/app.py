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


@app.route("/accounts/<int:_id>/orders", methods=["POST"])
def make_transaction(_id):

    try:

        time_now = int(time.time())
        date_now = datetime.fromtimestamp(time_now)

        zero_decimal = Decimal("0")

        # Check if request is working in operational times
        if date_now.hour < 6 or date_now.hour >= 15:
            raise ServiceNotAvailable

        operation = request.form["operation"]
        issuer_name = request.form["issuer_name"]
        _total_shares = request.form["total_shares"]
        _share_price = request.form["share_price"]

        # Check if operation is valid
        if operation not in ("sell", "buy"):
            raise InvalidOperationError

        # Casting parameters sent in request
        timestamp = int(request.form["timestamp"])
        total_shares = Decimal(_total_shares)
        share_price = Decimal(_share_price)

        # Check if parameters in request are valid numbers
        if total_shares <= zero_decimal or share_price <= zero_decimal:
            raise NegativeValuesError

        # Check if transaction was made 5 minutes ago
        is_transaction_repeated = cache.store_latest_transactions(
            _id, operation, issuer_name, _total_shares, 60*5
        )

        if not is_transaction_repeated:
            return flask.jsonify(
                get_response_body(
                    code=400,
                    data=dict(),
                    message="Something went wrong"
                )
            )

        # Check if timestamp is greater than now()
        if timestamp >= time_now:
            raise TimestampError

        last_tx = connector.get_last_transaction(_id, time_now)

        if timestamp <= int(last_tx["time"]):
            raise TimestampError

        # Check if user has the shares he is trying to sell
        if last_tx["operation"] == "account_created" and operation == "sell":
            raise NoStockError

        total_to_spend = total_shares * share_price

        # Check if user has enough balance
        user_balance_decimal = Decimal(last_tx["user_balance"])
        if user_balance_decimal < total_to_spend and operation == "buy":
            raise NotEnoughBalanceError

        last_issuer_tx = connector.get_last_transaction(_id, time_now, issuer_name)

        if operation == "sell" and total_shares > last_issuer_tx["user_shares"]:
            raise NoStockError

        if operation == "buy":
            arg_change_cash = -total_to_spend
            arg_change_shares = total_shares
            arg_user_balance = user_balance_decimal - total_to_spend
            arg_user_shares = last_issuer_tx["user_shares"] + total_shares

        else:
            arg_change_cash = total_to_spend
            arg_change_shares = -total_shares
            arg_user_balance = user_balance_decimal + total_to_spend
            arg_user_shares = last_issuer_tx["user_shares"] - total_shares

        _tx = Transaction(
            id=_id,
            time=str(timestamp),
            operation=operation,
            issuer_name=issuer_name,
            share_price=share_price,
            total_shares=total_shares,
            user_shares=arg_user_shares,
            change_cash=arg_change_cash,
            user_balance=arg_user_balance,
            change_shares=arg_change_shares,
        )

        connector.insert_item(_tx)
        user_transactions = connector.get_all_transactions_from_user(_id, time_now)
        return flask.jsonify(
            get_response_body(
                code=200,
                data={
                    "current_balance": {
                        "cash": str(arg_user_balance),
                        "issuers": user_transactions
                    }
                },
                message=""
            ))

    # Catch incomplete requests
    except (KeyError, ClientError) as e:
        return flask.jsonify(
            get_response_body(
                code=400,
                data=dict(),
                message=e
            ))

    # Transaction already made in the last 5 minutes
    except SameTransactionException as e:
        return flask.jsonify(
            get_response_body(
                code=425,
                data=dict(),
                message="Duplicate transactions are "
                        "not allowed"
            ))

    # Catch trade where user intends to sell without owning stocks
    except NoStockError:
        return flask.jsonify(
            get_response_body(
                code=403,
                data=dict(),
                message="You must own the stock "
                        "you are trying to sell"
            ))

    # Catch errors when user does not have balance
    except NotEnoughBalanceError:
        return flask.jsonify(
            get_response_body(
                code=403,
                data=dict(),
                message="Your balance is not enough to complete "
                        "this transaction"
            ))

    # Catch case where user is intending to request trade out of operational time
    except ServiceNotAvailable:
        return flask.jsonify(
            get_response_body(
                code=403,
                data=dict(),
                message="Service is not available right now. Retry "
                        "between a period of time of 6am and 3pm"
            ))

    except TimestampError:
        return flask.jsonify(
            get_response_body(
                code=400,
                data=dict(),
                message="Timestamp value is wrong. Use lower value "
                        "than now AND greater than your last transaction"
            )
        )

    # Data could not be caster correctly
    except NegativeValuesError:
        return flask.jsonify(
            get_response_body(
                code=400,
                data=dict(),
                message="Price or amount of shares should not "
                        "be negative or zero"
            ))

    # Transaction went wrong at database layer
    except ClientError:
        return flask.jsonify(
            get_response_body(
                code=400,
                data=dict(),
                message="Something went wrong with this operation. Please try again later"
            ))

    # Data could not be caster correctly
    except Exception as e:
        return flask.jsonify(
            get_response_body(
                code=400,
                data=dict(),
                message="Some parameters of request body are wrong. "
                        "Please check your parameters"
            ))
