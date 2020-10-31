import os
import boto3


def connect_dynamodb(table_name: str):

    try:

        return boto3.resource(
            'dynamodb',
            region_name=os.environ.get('REGION'),
            aws_access_key_id=os.environ.get('KEY'),
            aws_secret_access_key=os.environ.get('SECRET_KEY')
        ).Table(table_name)

    except Exception:

        raise
