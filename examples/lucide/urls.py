from django.urls import path
from views import icon_gallery

urlpatterns = [
    path("", icon_gallery),
]
