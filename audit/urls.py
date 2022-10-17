from django.urls import path, include
from rest_framework import routers
from audit.apis import get_current_balance

from audit.views import AuditView, ExpenseCategoryViewSet, ExpenseViewSet, Transaction


router = routers.DefaultRouter()

router.register("expense", ExpenseViewSet)
router.register("expense_category", ExpenseCategoryViewSet)

api_patterns = [
    path("get_current_balance/", get_current_balance.as_view()),
]

urlpatterns = [
    path("", include(router.urls)),
    path("audit/", AuditView.as_view(), name="audit"),
    path("transaction/", Transaction.as_view(), name="transaction"),
]+ api_patterns