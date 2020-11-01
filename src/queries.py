import os
from .utils import connect_dynamodb
from boto3.dynamodb.conditions import Key
from .errors import check_client_error

table = os.environ.get("TABLE")


class Queries(object):

    def __init__(self):

        self.db = connect_dynamodb(table)

    def get_last_user(self):

        result = self.db.query(
            KeyConditionExpression=
            Key("pk").eq("user")
            &
            Key("sk").gt("0"),
            ProjectionExpression="id",
            ScanIndexForward=False,
            Limit=1
        )

        check_client_error(
            result,
            "Query to get last user was not successful"
        )
        return result["Items"][0]["id"]


def put_element(item):
    return {
        "Item": item.__dict__,
        "TableName": table
    }
