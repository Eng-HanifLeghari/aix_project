from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, status
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenVerifySerializer
from django.utils.text import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.db import transaction
from .models import User, UserProfile, UserRoles
from django.contrib.auth import get_user_model


class UserSerialzer(serializers.ModelSerializer):
    """ """

    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "password",
            "password2",
            "role",
            "is_enable"
        )

    def validate(self, attrs):
        """

        :param attrs:
        :return:
        """
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    """
    For registering user profile
    """

    user = UserSerialzer()

    class Meta:
        model = UserProfile
        fields = (
            "member_id",
            "user",
        )

    @classmethod
    def create(cls, validated_data):
        """
        FOr registering user with his/her profile
        :param validated_data:
        :return:
        """
        user_profile_obj = ""
        user_created_status = False
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            user_data = validated_data.data.get("user")
            profile_data = validated_data.data
            profile_data.pop("user")
            if not UserRoles.objects.get(id=user_data.get("role")).role_key == 1:
                user = get_user_model().objects.create_user(**user_data)
            else:
                user_data.pop("role")
                user = get_user_model().objects.create_superuser(**user_data)
            # user.set_password(user_data.get("password"))
            user.save()
            user_profile = UserProfile.objects.create(user=user, **profile_data)
            if user_profile:
                user_created_status = True
                user_profile_obj = user_profile
                aix_response.update(
                    {
                        "statusMessage": "User registered successfully",
                        "statusCode": status.HTTP_201_CREATED,
                        "data": [],
                        "errorStatus": False,
                    }
                )
        except Exception as e:
            aix_response.update(
                {
                    "statusMessage": "Unable to create user with exception {}".format(
                        str(e)
                    ),
                    "statusCode": status.HTTP_417_EXPECTATION_FAILED,
                    "data": [],
                    "errorStatus": False,
                }
            )
            user_created_status = False
        finally:
            return user_created_status, user_profile_obj


class UpdateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "role",
            "is_enable",
        )


class UpdateUserProfileSerializer(serializers.ModelSerializer):
    user = UpdateUserSerializer()

    class Meta:
        model = UserProfile
        fields = (
            "title",
            "dob",
            "address",
            "country",
            "city",
            "zip",
            "phone",
            "user",
        )

    @classmethod
    def update(cls, instance, validated_data):
        user_updated_status = False
        try:
            with transaction.atomic():
                updated_user = validated_data.pop("user")
                User.objects.filter(id=instance.user_id).update(**updated_user)
                UserProfile.objects.filter(id=instance.id).update(**validated_data)
                user_updated_status = True
        except:
            user_updated_status = False
        finally:
            return user_updated_status


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """

    enter_new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        new_password = data["enter_new_password"]
        confirm_password = data["confirm_password"]
        if new_password != confirm_password:
            raise serializers.ValidationError("Both passwords are not same!")
        return data

    def validate_enter_new_password(self, value):
        validate_password(value)
        return value


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {"bad_token": _("Token is invalid or expired")}

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail("bad_token")


class VerifyTokenSerializer(TokenVerifySerializer):
    token = serializers.CharField()

    def validate(self, attrs):
        """
        Over-ridden method for token validation
        :param attrs:
        :return:
        """
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            super().validate(attrs)
            token = attrs["token"]
            aix_response.update(
                {
                    "statusMessage": "Token is Valid",
                    "data": {"token": token},
                    "statusCode": status.HTTP_302_FOUND,
                    "errorStatus": False,
                }
            )
        except Exception as e:
            # TokenObtainPairSerializer.get_token(user="")
            aix_response.update(
                {
                    "statusMessage": "Token is not Valid",
                    "data": [],
                    "statusCode": status.HTTP_303_SEE_OTHER,
                    "errorStatus": True,
                }
            )
        finally:
            return aix_response



# class RefreshTokenSerializer(TokenVerifySerializer):
#     token = serializers.CharField()
#
#     def validate(self, attrs):
#         """
#         Over-ridden method for token validation
#         :param attrs:
#         :return:
#         """
#         try:
#             super().validate(attrs)
#             token = attrs["token"]
#             AIX_RESPONSE.update(
#                 {
#                     "statusMessage": "Token is Valid",
#                     "data": {"token": token},
#                     "statusCode": status.HTTP_302_FOUND,
#                     "errorStatus": False,
#                 }
#             )
#         except Exception as e:
#             # TokenObtainPairSerializer.get_token(user="")
#             AIX_RESPONSE.update(
#                 {
#                     "statusMessage": "Token is not Valid",
#                     "data": [],
#                     "statusCode": status.HTTP_303_SEE_OTHER,
#                     "errorStatus": True,
#                 }
#             )
#         finally:
#             return AIX_RESPONSE


class UserListSerializer(serializers.ModelSerializer):
    """
    For listing all cameras
    """
    member_id = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    @staticmethod
    def get_name(obj):
        try:
            return obj.first_name
        except Exception as e:
            pass

    @staticmethod
    def get_role(obj):
        try:
            return obj.role.role_name
        except Exception as e:
            pass

    @staticmethod
    def get_member_id(obj):
        try:
            return obj.profile.member_id
        except Exception as e:
            pass

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "role",
            "name",
            "member_id",
            "is_enable"
        )


class UserRolesSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserRoles
        fields = "__all__"
