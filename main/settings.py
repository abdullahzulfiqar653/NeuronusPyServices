import os
import boto3
import environ
from pathlib import Path
from datetime import timedelta


env = environ.Env(
    ENV=(str, "DEV"),
    DEBUG=(bool, False),
    SECRET_KEY=(str, "False"),
    ALLOWED_HOSTS=(list, ["localhost"]),
    CORS_ORIGIN_ALLOW_ALL=(bool, False),
    CORS_ALLOW_CREDENTIALS=(bool, False),
)
BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

HOST_CONFIG = {
    "DEV": {
        "default": "dev.neuroadmin.azsoft.dev",
        "NeuroRsa": "dev.api.neurorsa.xyz",
        "NeuroDrive": "drive.api.azsoft.dev",
        "NeuroMail": "dev.api.neuromail.space",
        "PasswordManager": "dev.api.neuropassword.com",
    },
    "LIVE": {
        "default": "live.admin.azsoft.dev",
        "NeuroRsa": "live.api.neurorsa.xyz",
        "NeuroMail": "live.api.neuromail.space",
        "NeuroDrive": "live.api.neurodrive.com",
        "PasswordManager": "live.api.neuropassword.com",
    },
    "LOCAL": {
        "NeuroRsa": "rsa",
        "NeuroMail": "mail",
        "NeuroDrive": "drive",
        "default": "localhost",
        "PasswordManager": "pm",
    },
}

ENV = env("ENV")
DEBUG = env("DEBUG")
SECRET_KEY = env("SECRET_KEY")
ACTIVE_HOSTS = HOST_CONFIG[ENV]
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
CORS_EXPOSE_HEADERS = ["Content-Disposition"]
CORS_ORIGIN_ALLOW_ALL = env("CORS_ORIGIN_ALLOW_ALL")
CORS_ALLOW_CREDENTIALS = env("CORS_ALLOW_CREDENTIALS")

DEFAULT_HOST = "default"
ROOT_HOSTCONF = "main.hosts"

MAIL_SERVER = env("MAIL_SERVER")
MAIL_SERVER_API_KEY = env("MAIL_SERVER_API_KEY")
MAIL_SERVER_BASE_URL = env("MAIL_SERVER_BASE_URL")

S3_CLIENT = boto3.client(
    "s3",
    region_name=env("DIGITALOCEAN_REGION"),
    endpoint_url=env("DIGITALOCEAN_BUCKET_URL"),
    aws_access_key_id=env("DIGITALOCEAN_ACCESS_KEY"),
    aws_secret_access_key=env("DIGITALOCEAN_BUCKET_SECRET_KEY"),
)
DIGITALOCEAN_SPACE_NAME = env("DIGITALOCEAN_SPACE_NAME")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework_simplejwt",
    # 3rd party apps
    "drf_yasg",
    "corsheaders",
    "rest_framework",
    "django_filters",
    # user defined apps
    "main",
    "NeuroRsa",
    "NeuroMail",
    "NeuroDrive",
    "PasswordManager",
]


MIDDLEWARE = [
    "django_hosts.middleware.HostsRequestMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_hosts.middleware.HostsResponseMiddleware",
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

ROOT_URLCONF = "main.urls"

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

WSGI_APPLICATION = "main.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": env("DB_ENGINE", default="django.db.backends.sqlite3"),
        "NAME": env("DB_NAME", default=os.path.join(BASE_DIR, "db.sqlite3")),
        "USER": env("DB_USER", default=""),
        "PASSWORD": env("DB_PASSWORD", default=""),
        "HOST": env("DB_HOST", default=""),
        "PORT": env("DB_PORT", default=""),
    }
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "main.pagination.CustomPagination",
}

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter your token in the format: (Bearer <apiKey>) Example: Bearer eycdefghijklmnopqrstuvwxyz...",
        },
    },
    "USE_SESSION_AUTH": False,
    "DEFAULT_AUTO_SCHEMA_CLASS": "drf_yasg.inspectors.SwaggerAutoSchema",
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(weeks=50),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=52),
}

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


USE_TZ = True
USE_I18N = True
TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"


STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
