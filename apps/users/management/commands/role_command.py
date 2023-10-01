from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.users.models import UserRoles


class Command(BaseCommand):
    help = "Create User Roles"

    def handle(self, *args, **kwargs):
        UserRoles.objects.get_or_create(id=1, role_key=1, role_name="Mission Commander")
        UserRoles.objects.get_or_create(
            id=2, role_key=2, role_name="Reconnaissance Officer"
        )
        UserRoles.objects.get_or_create(
            id=3, role_key=3, role_name="Surveillance Officer"
        )
        roles = UserRoles.objects.all()
        for role in roles:
            print(role.role_name)
