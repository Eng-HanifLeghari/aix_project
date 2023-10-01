from django.contrib import admin

from apps.data_source.models import DataSource, DataSourceResponse

# Register your models here.
admin.site.register(DataSource)
admin.site.register(DataSourceResponse)
