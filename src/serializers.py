from boto3.dynamodb.types import TypeSerializer
from decimal import Decimal

serializer = TypeSerializer()


def serialize(data):

    if isinstance(data, Decimal):

        return serializer.serialize(data)

    if isinstance(data, str):

        return serializer.serialize(data)

    if isinstance(data, list):

        return [serialize(v)['M'] for v in data]

    if isinstance(data, dict):

        try:
            return serializer.serialize(data)['M']
        except TypeError:
            return {key: serialize(data[key]) for key in data}
    else:
        return data
