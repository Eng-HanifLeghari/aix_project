from django.contrib.auth.base_user import BaseUserManager
from django.apps import apps


class UserManager(BaseUserManager):
    """
    User management for create, update and delete
    """

    def create_user(
        self, email, username, password, first_name=None, last_name=None, role=None, is_enable=None
    ):
        """
        Creating user
        :param is_enable:
        :param role:
        :param last_name:
        :param first_name:
        :param email:
        :param username:
        :param password:
        :return: user object
        """
        if not email:
            raise ValueError("ENTER AN EMAIL BUDDY")
        if not username:
            raise ValueError("I KNOW YOU HAVE A NAME")
        if not password:
            raise ValueError("PASSWORD?!?!?!? HELLO??")
        UserRoles = apps.get_model("users.UserRoles")
        role = UserRoles.objects.get(role_key=role)
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_enable=is_enable,
        )
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = False
        user.save()

        return user

    def create_superuser(
        self, email, username, password, first_name=None, last_name=None, is_enable=None
    ):
        """
        For creating superuser
        :param is_enable:
        :param last_name:
        :param first_name:
        :param email:
        :param username:
        :param password:
        :return: user object
        """

        user = self.create_user(
            email, username, password, first_name, last_name, role=1, is_enable=is_enable
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_enable = True
        user.save()
        return user

    def create_inactive_user(
        self, username, email, password, first_name=None, last_name=None
    ):
        """
        IN-active user
        :param last_name:
        :param first_name:
        :param username:
        :param email:
        :param password:
        :return: user object
        """
        user = self.create_user(email, username, password, first_name, last_name)
        user.is_active = False
        user.save()
        return user
