from django.shortcuts import render

from django_iconx.conf import get_settings
from django_iconx.svg import discover


def icon_gallery(request):
    icon_settings = get_settings()
    icons = sorted(discover(icon_settings).icons)
    return render(request, "gallery.html", {"icons": icons, "prefix": icon_settings.prefix})
