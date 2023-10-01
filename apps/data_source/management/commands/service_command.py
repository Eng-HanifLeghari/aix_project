from django.core.management.base import BaseCommand
from apps.data_source.models import AIServices


class Command(BaseCommand):
    help = "Create services"

    def handle(self, *args, **kwargs):
        """
        For creating services

        :param args:
        :param kwargs:
        :return:
        """
        AIServices.objects.get_or_create(id=1, service_key="object_detection", service_name="Object Detection")
        AIServices.objects.get_or_create(id=2, service_key="drone_detection", service_name="Drone Detection")

