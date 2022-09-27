from django.urls import path, include
from tracking.views import log_coordinates
urlpatterns = [
    path("", log_coordinates.as_view()),
]
