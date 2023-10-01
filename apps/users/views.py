from django.contrib.auth import authenticate, login
from rest_framework import generics
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)
from .serializers import RefreshTokenSerializer, UserListSerializer, UserRolesSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import User, UserProfile
from .serializers import (
    RegisterSerializer,
    ChangePasswordSerializer,
    UpdateUserProfileSerializer,
)
from .utils.token_manager import get_tokens_for_user
from .controllers import UserController


class LoginView(APIView):
    """
    Login View
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """

        :param request:
        :return: Tokens , User, Message
        """
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)

        if "email" not in request.data or "password" not in request.data:
            aix_response = {
                    "statusMessage": "Credentials missing",
                    "data": [],
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorStatus": True,
                }
        else:
            email = request.data.get("email")
            password = request.data.get("password")
            user = authenticate(request, email=email, password=password)
            if user is not None and user.is_active and user.is_enable:
                login(request, user)
                auth_data = get_tokens_for_user(request.user)
                auth_data["user_id"] = user.id
                auth_data["user_role"] = user.role.role_key
                auth_data["user_name"] = user.username
                # latest_token_id = OutstandingToken.objects.filter(user=user).order_by("-created_at").first().id
                # OutstandingToken.objects.filter(user=user).exclude(pk=latest_token_id).delete()
                aix_response = {
                        "statusMessage": "Login Success",
                        "statusCode": status.HTTP_200_OK,
                        "data": auth_data,
                        "errorStatus": False,
                    }
            else:
                aix_response = {
                        "statusMessage": "Unauthorized access: Invalid username or password",
                        "statusCode": 401,
                        "data": [],
                        "errorStatus": True,
                    }
        return Response(aix_response)


class UserSignUp(APIView):
    """
    User signup view
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    response_dict = {}

    def post(self, request):
        """
        For creating new user
        :param request:
        :return:
        """
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)

        try:
            validated_data = RegisterSerializer(data=request.data)
            if validated_data.is_valid():
                user_created_status, user_profile_obj = RegisterSerializer.create(
                    validated_data=validated_data
                )
                if user_created_status:
                    aix_response = {
                            "statusMessage": "User registered successfully",
                            "statusCode": status.HTTP_201_CREATED,
                            "data": [],
                            "errorStatus": False,
                        }
            else:
                aix_response = {
                        "statusMessage": "Invalid data",
                        "statusCode": status.HTTP_417_EXPECTATION_FAILED,
                        "data": validated_data.errors,
                        "errorStatus": True,
                    }
        except Exception as e:
            self.response_dict["msg"] = str(e)
            self.response_dict["response_status"] = False
            aix_response = {
                    "statusMessage": str(e),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)


class UpdateUser(APIView):
    """
    User update view
    """
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    response_dict = {}

    def patch(self, request, user_id, *args, **kwargs):
        """
        For updating user
        :param user_id:
        :param request:
        :return:
        """
        kwargs['partial'] = True
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)

        try:
            instance = UserProfile.objects.select_related("user").get(id=user_id)
            validated_data = UpdateUserProfileSerializer(data=request.data)
            if validated_data.is_valid():
                user_updated_status = UpdateUserProfileSerializer.update(instance, validated_data=validated_data.data)
                if user_updated_status:
                    aix_response = {
                            "statusMessage": "User updated successfully",
                            "statusCode": status.HTTP_200_OK,
                            "data": validated_data.data,
                            "errorStatus": False,
                        }
                else:
                    aix_response = {
                            "statusMessage": "Unable to update",
                            "statusCode": status.HTTP_417_EXPECTATION_FAILED,
                            "data": validated_data.errors,
                            "errorStatus": True,
                        }
            else:
                aix_response = {
                        "statusMessage": "Given data is not validated!",
                        "statusCode": status.HTTP_417_EXPECTATION_FAILED,
                        "data": validated_data.errors,
                        "errorStatus": True,
                    }
        except Exception as e:
            self.response_dict["msg"] = str(e)
            self.response_dict["response_status"] = False
            aix_response = {
                    "statusMessage": str(e),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)


class UpdatePassword(APIView):
    """
    An endpoint for changing password.
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]

    def get_object(self, queryset=None):
        return self.request.user

    def put(self, request, *args, **kwargs):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        self.object = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            self.object.set_password(serializer.data.get("enter_new_password"))
            self.object.save()
            aix_response = {
                "statusMessage": "Password updated successfully!",
                "data": [],
                "errorStatus": False,
                "statusCode": status.HTTP_200_OK
            }
            return Response(aix_response)

        aix_response = {
            "statusMessage": serializer.errors,
            "data": [],
            "errorStatus": True,
            "statusCode": status.HTTP_400_BAD_REQUEST
        }
        return Response(aix_response)


class LogoutView(GenericAPIView):
    serializer_class = RefreshTokenSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            sz = self.get_serializer(data=request.data)
            sz.is_valid(raise_exception=True)
            sz.save()
            aix_response = {
                    "statusMessage": "User Logged out",
                    "statusCode": status.HTTP_200_OK,
                    "data": [],
                    "errorStatus": False,
                }
        except Exception as e:
            aix_response = {
                    "statusMessage": str(e),
                    "statusCode": status.HTTP_417_EXPECTATION_FAILED,
                    "data": [],
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)


class DeleteTokens(GenericAPIView):
    serializer_class = RefreshTokenSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)

    def post(self, request, *args):
        try:
            BlacklistedToken.objects.all().delete()
            OutstandingToken.objects.all().delete()

            aix_response = {
                    "statusMessage": "Token Deleted",
                    "statusCode": status.HTTP_200_OK,
                    "data": [],
                    "errorStatus": False,
                }
        except Exception as e:
            aix_response = {
                    "statusMessage": str(e),
                    "statusCode": status.HTTP_417_EXPECTATION_FAILED,
                    "data": [],
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)


class UserList(generics.ListAPIView):
    """

    API for getting list of required data
    @param : No params
    @returns: returns list
    @raises Exception: Not found exception

    """

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)
    serializer_class = UserListSerializer
    pagination_class = None
    model = serializer_class.Meta.model

    def get_queryset(self):
        queryset = (self.model.objects.filter(is_active=True).exclude(id=self.request.user.id)).order_by("-created_at")
        return queryset

    def list(self, request, *args, **kwargs):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)

        try:
            if request.user.is_superuser:
                res = super(UserList, self).list(request, *args, **kwargs)
                if res.data:
                    aix_response = {
                            "statusMessage": "Data fetched successfully",
                            "errorStatus": False,
                            "data": res.data,
                            "statusCode": status.HTTP_200_OK,
                        }
                else:
                    aix_response ={
                            "statusMessage": "No Data",
                            "errorStatus": False,
                            "data": res.data,
                            "statusCode": status.HTTP_200_OK,
                        }
            else:
                aix_response = {
                        "statusMessage": "Permission denied. Only super users can access list of all users",
                        "errorStatus": False,
                        "data": [],
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                    }
        except Exception as err:
            aix_response = {
                    "statusMessage": str(err),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)


class DeleteUser(APIView):
    """
    Delete API
    """
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]

    def delete(self, request, user_id=None):
        """
        For calling delete_user controller
        :param user_id:
        :param request:
        :return:
        """
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)

        try:

            if User.objects.filter(id=user_id, role__role_key=1).first():
                aix_response = {
                        "statusMessage": "Mission Commander can not be deleted!",
                        "data": [],
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "errorStatus": True,
                    }
            else:
                aix_response = UserController.delete_user(request, user_id)
        except Exception as e:
            aix_response = {
                    "statusMessage": "User deletion failed with exception {}".format(str(e)),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return Response(aix_response)


class UserStatus(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request, user_id=None):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            aix_response = User.user_status(user_id)
        except Exception as e:
            aix_response = {
                    "statusMessage": "User update status failed with exception {}".format(str(e)),
                    "errorStatus": False,
                    "data": [],
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                }
        finally:
            return Response(aix_response)


class UserRolesListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)
    serializer_class = UserRolesSerializer

    def get(self, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            aix_response = UserController.get_role_list()
        except Exception as e:
            aix_response = {
                    "statusMessage": "User roles not found, error is {}".format(str(e)),
                    "errorStatus": False,
                    "data": [],
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                }
        finally:
            return Response(aix_response)


class EmailChecker(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            aix_response = UserController.email_checker(request)
        except Exception as e:
            aix_response = {
                    "statusMessage": str(e),
                    "errorStatus": False,
                    "data": [],
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                }
        finally:
            return Response(aix_response)
