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


def parse_user(obj):
    obj["id"] = str(obj["id"])
    obj["cash"] = str(obj["cash"])
    obj["issuers"] = []
    obj.pop("pk")
    obj.pop("sk")
    return obj
