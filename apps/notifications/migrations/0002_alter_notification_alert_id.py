# Generated by Django 4.1.5 on 2023-05-23 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="alert_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
