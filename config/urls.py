"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.urls import re_path

import config.settings.base

schema_view = config.settings.base.schema_view
urlpatterns = [
    ############### ------- For Admin panel -------- ####################
    re_path(r"^admin/", admin.site.urls),
    ############### ------- Swagger------------- ##################
    path(
        "swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    ############### ------- For apps url ------------- ####################
    re_path(r"^users/", include("apps.users.urls")),
    re_path(r"^data-source/", include("apps.data_source.urls")),
    re_path(r"^camera/", include("apps.camera.urls")),
    re_path(r"^notifications/", include("apps.notifications.urls")),
    re_path(r"^reconnaissance/", include("apps.reconnaissance.urls"))
]
