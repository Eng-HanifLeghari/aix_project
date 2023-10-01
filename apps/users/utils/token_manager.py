from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    """

    :param user:
    :return: Access and Refresh Token
    """
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
