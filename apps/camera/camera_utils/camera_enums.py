from enum import Enum
from django.db import models
from django.utils.translation import gettext_lazy as _


class Priorities(Enum):
    High = 1
    Medium = 2
    Low = 3


class Blue_Force(Enum):
    Soldier = 3
    Military_Vehicle = 4
    Military_Tanks = 2
    Military_Truck = 5


class Red_Force(Enum):
    Civilian_Vehicle = 1
    Person = 8
    Pistol = 7
    Gun = 6
    Drone = 9


class Threats(Enum):
    Civilian_Vehicle = 1
    Military_Tanks = 2
    Soldier = 3
    Military_Vehicle = 4
    Military_Truck = 5
    Gun = 6
    Pistol = 7
    Person = 8
    Drone = 9


class ThreatsStrings(Enum):
    Civilian_Vehicle = "Civilian Vehicle"
    Military_Tanks = "Military Tanks"
    Soldier = "Soldier"
    Military_Vehicle = "Military Vehicle"
    Military_Truck = "Military Truck"
    Gun = "Gun"
    Pistol = "Pistol"
    Person = "Person"
    Drone = "Drone"


class Protocol(models.TextChoices):
    RTSM = "rtsm", _("RTSM")
    RTMP = "rtmp", _("RTMP")


PROTOCOL_CHOICES = (
    ('rtsp', 'rtsp'),
    ('rtmp', 'rtmp'),
)
