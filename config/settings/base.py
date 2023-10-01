import os
import environ
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
APPS_DIR = os.path.join(BASE_DIR, "apps")


def base_dir_join(*args):
    return os.path.join(BASE_DIR, *args)


def apps_dir_join(*args):
    return os.path.join(APPS_DIR, *args)


# Base
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
DEBUG = os.getenv("DEBUG")
TIME_ZONE = os.getenv("TIME_ZONE")
LANGUAGE_CODE = "en-us"
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True
DATETIME_FORMAT = "%d/%m/%Y %H:%M"

DJANGO_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "corsheaders",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "rest_framework",
    "rest_framework_gis",
    "rest_framework_simplejwt",
    "channels",
    "rest_framework_simplejwt.token_blacklist",
    "drf_yasg",
]
THIRD_PARTY_APPS = []

LOCAL_APPS = [
    "apps.users",
    "apps.data_source",
    "apps.camera",
    "apps.notifications",
    "apps.reconnaissance"
    # 'apps.data_source.apps.DataSourceConfig',
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "customutils.customMiddleware.DisableCSRFMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "customutils.middleware.ResponseFormatMiddleware"
]
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    "http://localhost:8000",
    "http://192.168.25.101:3000",
    "http://192.168.25.157:8000",
)

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    # "x-csrftoken",
    "x-requested-with",
]

ROOT_URLCONF = "config.urls"
ALLOWED_HOSTS = ["*"]
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        # "BACKEND": "channels_redis.pubsub.RedisPubSubChannelLayer",
        "CONFIG": {
            "hosts": [(os.getenv("REDIS_HOST"), 6379)],
            "capacity": 1500,  # default 100
            "expiry": 10,
        },
    },
}

# Auth user model
AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
STATIC_URL = "static/"

# Setting up auth

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
        "rest_framework.permissions.AllowAny",
    ),
    'COERCE_DECIMAL_TO_STRING': False,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

# Simple JWT configuration

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

# Logging
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'console': {
#             'format': '%(name)-12s %(levelname)-8s %(message)s'
#         },
#         'file': {
#             'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
#         }
#     },
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#             'formatter': 'console'
#         },
#         'file': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'formatter': 'file',
#             'filename': 'logfiles/debug.log'
#         }
#     },
#     'loggers': {
#         '': {
#             'level': 'DEBUG',
#             'handlers': ['console', 'file']
#         }
#     }
# }


REST_USE_JWT = True

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SWAGGER_SETTINGS = {
    "VALIDATOR_URL": "http://localhost:8189",
}
schema_view = get_schema_view(
    openapi.Info(
        title="Smart API",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)
from glob import glob

GDAL_LIBRARY_PATH = glob(os.getenv("GDAL_LIBRARY_PATH"))[0] if glob(os.getenv("GDAL_LIBRARY_PATH")) else None
GEOS_LIBRARY_PATH = glob(os.getenv("GEOS_LIBRARY_PATH"))[0] if glob(os.getenv("GEOS_LIBRARY_PATH")) else None

