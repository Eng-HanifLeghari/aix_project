# Generated by Django 4.0.5 on 2023-06-05 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reconnaissance', '0002_imageserverdata_base_folder'),
    ]

    operations = [
        migrations.AddField(
            model_name='imageserverdata',
            name='layer_name',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
    ]
