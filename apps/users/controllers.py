from django.contrib.auth import get_user_model
from apps.users.models import UserRoles
from apps.users.serializers import UserRolesSerializer
from rest_framework import status
from customutils.request_handlers import RequestHandler

User = get_user_model()


class UserController:

    @classmethod
    def delete_user(cls, request, user_id):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            if request.user.id == user_id or request.user.is_superuser:
                delete_status = User.user_deletion(user_id)
                if delete_status:
                    aix_response = {
                            "statusMessage": "User Deleted successfully",
                            "errorStatus": False,
                            "data": [],
                            "statusCode": status.HTTP_204_NO_CONTENT,
                        }
            else:
                aix_response = {
                        "statusMessage": "You don't have permission to delete this user",
                        "errorStatus": True,
                        "data": [],
                        "statusCode": status.HTTP_403_FORBIDDEN,
                    }
        except Exception as err:
            aix_response = {
                    "statusMessage": str(err),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return aix_response

    @classmethod
    def get_role(cls, request):
        role = None
        try:
            role_key = RequestHandler.get_request_data(request=request , key="role_key")
            role = UserRoles.get_role(role_key=role_key)
        except:
            pass
        finally:
            pass

    @classmethod
    def get_role_list(cls):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            roles = UserRoles.roles_list()
            serializer_data = UserRolesSerializer(roles, many=True)
            aix_response.update(
                {
                    "statusMessage": "User roles list",
                    "errorStatus": True,
                    "data": serializer_data.data,
                    "statusCode": status.HTTP_200_OK,
                }
            )
        except Exception as e:
            aix_response.update(
                {
                    "statusMessage": "User roles not found, error is {}".format(str(e)),
                    "errorStatus": True,
                    "data": [],
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                }
            )
        finally:
            return aix_response

    @classmethod
    def email_checker(cls, request):
        try:
            email = RequestHandler.get_request_data(request, "email")
            instance = User.objects.filter(email=email).first()
            if instance is None:
                aix_response = {
                        "statusMessage": "You did right job!",
                        "errorStatus": False,
                        "data": [],
                        "statusCode": status.HTTP_200_OK,
                    }
            else:
                aix_response = {
                        "statusMessage": "This email has already taken!",
                        "errorStatus": True,
                        "data": [],
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                    }
        except Exception as e:
            aix_response = {
                    "statusMessage": str(e),
                    "errorStatus": True,
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
        finally:
            return aix_response
