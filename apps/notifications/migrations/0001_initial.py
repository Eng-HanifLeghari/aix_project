# Generated by Django 4.1.5 on 2023-05-22 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_created=True, auto_now_add=True),
                ),
                ("alert_id", models.UUIDField(blank=True, null=True)),
                ("text", models.TextField(blank=True, max_length=1024, null=True)),
                ("threat", models.CharField(blank=True, max_length=255, null=True)),
                ("priority", models.CharField(blank=True, max_length=255, null=True)),
                ("camera_ip", models.CharField(blank=True, max_length=25, null=True)),
                ("is_read", models.BooleanField(blank=True, default=False, null=True)),
                (
                    "camera_name",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "lat",
                    models.DecimalField(decimal_places=6, default=0.0, max_digits=9),
                ),
                (
                    "lng",
                    models.DecimalField(decimal_places=6, default=0.0, max_digits=9),
                ),
                ("updated_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
