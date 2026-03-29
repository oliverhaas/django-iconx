from django.shortcuts import render

from django_iconx.conf import get_settings
from django_iconx.svg import discover_svgs


def icon_gallery(request):
    icon_settings = get_settings()
    icons = sorted(discover_svgs(icon_settings).keys())
    return render(request, "gallery.html", {"icons": icons, "prefix": icon_settings.prefix})
