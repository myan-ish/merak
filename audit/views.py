from rest_framework.viewsets import ModelViewSet
from audit.models import Expense, ExpenseCategory, Ledger
from rest_framework.views import APIView
from audit.serializer import ExpenseCategorySerializer, ExpenseSerializer
from django.views.generic.base import View
from django.shortcuts import render
 

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

class AuditView(View):
    template_name = "audit.html"
    
    def get(self, request):
        context = {
        "ledger": Ledger.objects.all(),
        }
        return render(request, self.template_name, context=context)

class AuditApi(APIView):

    def post(self, request,id):
        print(request.data)
        ledger = Ledger.objects.get(id=id)
        ledger.amount = request.data["amount"]
        