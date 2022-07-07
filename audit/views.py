from rest_framework.viewsets import ModelViewSet
from audit.models import Expense, ExpenseCategory

from audit.serializer import ExpenseCategorySerializer, ExpenseSerializer


class ExpenseViewSet(ModelViewSet):
    serializer_class = ExpenseSerializer
    queryset = Expense.objects.all()

    def get_queryset(self):
        print(self.queryset.filter(organization=self.request.user.organization))
        return self.queryset.filter(organization=self.request.user.organization)


class ExpenseCategoryViewSet(ModelViewSet):
    serializer_class = ExpenseCategorySerializer
    queryset = ExpenseCategory.objects.all()

    def get_queryset(self):
        return self.queryset.filter(organization=self.request.user.organization)
