from audit.models import Ledger
from django.db.models import Sum
from rest_framework.response import Response
from rest_framework.views import APIView

class get_current_balance(APIView):
    '''
    Returns the current audit balance
    '''
    def get(self, request):
        current_balance = Ledger.objects.aggregate(Sum('closing_balance'))
        return Response({"current_balance": current_balance})
