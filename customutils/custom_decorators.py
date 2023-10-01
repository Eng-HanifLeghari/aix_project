from rest_framework import status
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from customutils.generic_response import AIX_RESPONSE


def is_user_loggedin():
    def decorator(func):
        def wrapper(method, *args, **kwargs):
            # todo Need to modify
            refresh_token = RefreshToken.for_user(method.request.user)
            # refresh_token = method.request.headers.get('Refresh', None)
            refresh_token = RefreshToken("")
            # refresh_token.check_blacklist()
            # outstanding_token = OutstandingToken.objects.filter(user=method.request.user).first()
            # token = outstanding_token.token
            if not refresh_token.check_blacklist():
                return func(method, *args, **kwargs)
            else:
                AIX_RESPONSE.update(
                    {
                        "statusMessage": "Unauthorized Access",
                        "errorStatus": True,
                        "data": [],
                        "statusCode": status.HTTP_401_UNAUTHORIZED,
                    }
                )
                return Response(AIX_RESPONSE)

        return wrapper

    return decorator
