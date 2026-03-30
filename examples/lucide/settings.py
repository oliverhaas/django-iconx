from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = "example-secret-key-not-for-production"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "django_iconx",
]

ROOT_URLCONF = "urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
    },
]

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

ICONX = {
    "sets": {
        "": "icons/lucide/",
    },
    "output": str(BASE_DIR / "static" / "iconx" / "icons.css"),
    "mode": "data_uri",
    "prefix": "icon",
    "size": "1em",
}
