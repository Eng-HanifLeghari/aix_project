from django.db import models
from django.utils.translation import gettext_lazy as _


class DataTypeChoices(models.TextChoices):
    AUDIO = "Au", _("Audio")
    VIDEO = "Vd", _("Video")
    IMAGE = "Im", _("Image")
    SATELLITE = "St", _("Satellite")
