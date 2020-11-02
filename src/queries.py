import os
import redis
from .utils import connect_dynamodb
from boto3.dynamodb.conditions import Key, Attr
from .errors import check_client_error
from .custom_exceptions import SameTransactionException

table = os.environ.get("TABLE")


class Queries(object):

    def __init__(self):

        self.db = connect_dynamodb(table)

    def get_last_user(self):
        try:
            result = self.db.query(
                KeyConditionExpression=
                Key("pk").eq("user"),
                ProjectionExpression="id",
                ScanIndexForward=False,
            )
            check_client_error(
                result,
                "Query to get last user was not successful"
            )
            return result["Items"][0]["id"]
        except IndexError:
            return 0

    def insert_item(self, _item):

        result = self.db.put_item(
            Item=_item.__dict__
        )
        check_client_error(
            result,
            "Insert of item was not successful"
        )

    def get_last_transaction(self, _id, timestamp, _issuer=""):

        if not _issuer:
            sk = Key("sk").lt(f"issuer#{timestamp}")
            project_expression = "#t, operation, user_balance"
        else:
            sk = Key("sk").lt(f"issuer#{timestamp}#{_issuer}")
            project_expression = "#t, total_shares, user_shares, user_balance"

        result = self.db.query(
            KeyConditionExpression=
            Key("pk").eq(f"transaction#{_id}")
            & sk,
            ProjectionExpression=project_expression,
            ScanIndexForward=False,
            ExpressionAttributeNames={"#t": "time"},
            Limit=1
        )
        check_client_error(
            result,
            "Query to get last transaction was not successful"
        )
        return result["Items"][0]

    def get_all_transactions_from_user(self, _id, timestamp):

        items = list()
        result = self.db.query(
            KeyConditionExpression=
            Key("pk").eq(f"transaction#{_id}")
            & Key("sk").lt(f"issuer#{timestamp}"),
            ProjectionExpression="issuer_name, total_shares, share_price",
            ScanIndexForward=False
        )
        items += result["Items"]

        while 'LastEvaluatedKey' in result:
            result = self.db.query(
                KeyConditionExpression=
                Key("pk").eq(f"transaction#{_id}")
                & Key("sk").lt(f"issuer#{timestamp}"),
                ProjectionExpression="issuer_name, total_shares, share_price",
                ExclusiveStartKey=result["LastEvaluatedKey"],
                ScanIndexForward=False
            )

            if "Items" in result:
                items += result["Items"]
            else:
                raise KeyError("There was an error fetching open orders.")

        to_delete = None
        for item in items:
            item["total_shares"] = str(item["total_shares"])
            item["share_price"] = str(item["share_price"])
            if not item["issuer_name"]:
                to_delete = item
        items.remove(to_delete)

        return items


class RedisDB(object):

    def __init__(self):

        self.inst = redis.Redis(
            host=os.environ.get("REDIS_HOST"),
            port=os.environ.get("REDIS_PORT"),
            db=0)

    def store_latest_transactions(self, _id, _operation,
                                  _issuer, _amount, ex_time):
        value = self.inst.get(f"{_id}#{_issuer}#{_operation}#{_amount}")
        if value:
            raise SameTransactionException(
                "Same transaction was done in a span of 5 minutes before"
            )

        result = self.inst.set(
            f"{_id}#{_issuer}#{_operation}#{_amount}", 1, ex=ex_time)
        return result


def put_element(item):
    return {
        "Item": item.__dict__,
        "TableName": table
    }
