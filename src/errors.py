
from botocore.exceptions import ClientError


def get_response_body(code, data, message):
    return {
        "HTTPResponse": code,
        "data": data,
        "message": message
    }


def check_client_error(_result, _response):
    if _result["ResponseMetadata"]["HTTPStatusCode"] != 200:
        raise ClientError(
            operation_name=f"HTTPCode-{_result['HTTPStatusCode']}",
            error_response=_response
        )
