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
