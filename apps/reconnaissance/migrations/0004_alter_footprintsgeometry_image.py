# Generated by Django 4.0.5 on 2023-06-05 12:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reconnaissance', '0003_imageserverdata_layer_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='footprintsgeometry',
            name='image',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='image_server_data', to='reconnaissance.imageserverdata'),
        ),
    ]
