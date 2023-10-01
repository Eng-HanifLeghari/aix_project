from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from rest_framework import status
from apps.users.usermanager import UserManager
from django.shortcuts import get_object_or_404


class UserRoles(models.Model):
    """
    For defining roles
    """

    id = models.IntegerField(primary_key=True)
    role_key = models.PositiveSmallIntegerField(blank=True, null=True)
    role_name = models.CharField(blank=True, null=True, max_length=40)

    @classmethod
    def get_role(cls, role_key=None):
        return get_object_or_404(UserRoles, role_key=role_key)

    @classmethod
    def roles_list(cls):
        return UserRoles.objects.all()



class User(AbstractBaseUser, PermissionsMixin):
    """
    Base User model
    """

    username = models.CharField(blank=True, null=True, max_length=25)
    email = models.EmailField(_("email address"), unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    is_enable = models.BooleanField(default=True, null=True, blank=True)
    role = models.ForeignKey(
        UserRoles,
        on_delete=models.SET_NULL,
        related_name="user_role",
        null=True,
        blank=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    objects = UserManager()

    def __str__(self):
        return "{}".format(self.email)

    @classmethod
    def user_deletion(cls, user_id):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        delete_status = False
        try:
            obj = User.objects.get(id=user_id)
            obj.is_active = False
            obj.save()
            delete_status = True
        except Exception as e:
            aix_response.update(
                {
                    "statusMessage": "Object not found.",
                    "errorStatus": True,
                    "data": [],
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                }
            )
        finally:
            return delete_status, aix_response

    @classmethod
    def user_status(cls, user_id):
        try:
            instance = User.objects.get(id=user_id)
            if instance:
                if instance.is_enable:
                    instance.is_enable = False
                    instance.save()
                    aix_response = {
                            "statusMessage": f"Access Denied",
                            "errorStatus": False,
                            "data": str(instance),
                            "statusCode": status.HTTP_200_OK,
                        }
                else:
                    instance.is_enable = True
                    instance.save()
                    aix_response = {
                            "statusMessage": f"Access Granted",
                            "errorStatus": False,
                            "data": str(instance),
                            "statusCode": status.HTTP_200_OK,
                        }
            else:
                aix_response = {
                        "statusMessage": "User not found!",
                        "errorStatus": False,
                        "data": [],
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                    }
        except Exception as e:
            aix_response = {
                    "statusMessage": "User update status failed with exception {}".format(str(e)),
                    "errorStatus": False,
                    "data": [],
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                }
        finally:
            return aix_response


class UserProfile(models.Model):
    """
    User profile Model
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    title = models.CharField(max_length=50, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    zip = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    member_id = models.CharField(max_length=50, unique=True)
    date_joined = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    # photo = models.ImageField(upload_to='uploads', blank=True)
