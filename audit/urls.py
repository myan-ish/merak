from django.urls import path, include
from rest_framework import routers

from audit.views import ExpenseViewSet


router = routers.DefaultRouter()

router.register("expense", ExpenseViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
