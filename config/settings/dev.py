from config.settings.base import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}

# FTP Server configurations
FTP_SERVER = "10.100.150.105"
FTP_PORT = 80
FTP_USERNAME = "microcrawler"
FTP_PASSWORD = "rapidev"
BASE_PATH = "/home/microcrawler/AiX/Media/"
