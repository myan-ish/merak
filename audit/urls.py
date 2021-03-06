from django.urls import path, include
from rest_framework import routers

from audit.views import ExpenseCategoryViewSet, ExpenseViewSet


router = routers.DefaultRouter()

router.register("expense", ExpenseViewSet)
router.register("expense_category", ExpenseCategoryViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
