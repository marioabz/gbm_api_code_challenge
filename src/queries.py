import os
from utils import connect_dynamodb, dynamodb_client
from boto3.dynamodb.conditions import Key
from serializers import serialize

table = os.environ.get("TABLE")


class Queries(object):

    def __init__(self):

        self.db = connect_dynamodb(table)

    def get_last_user(self):
        return self.db.query(
            KeyConditionExpression=
            Key("pk").eq("users")
            &
            Key("sk").gt("0"),
            ProjectionExpression="sk",
            ScanIndexForward=False,
            Limit=1
        )

    def register_user(self, user):
        return self.db.put_item(
            Item=user.__dict__
        )
