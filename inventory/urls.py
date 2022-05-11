from django.urls import path, include
from rest_framework import routers

from inventory.views import AcceptOrderView, DeclineAcceptedOrderView, DeclineAssignedOrderView, OrderView, ProductView

router = routers.DefaultRouter()

router.register('product',ProductView)
router.register('order' ,OrderView)

urlpatterns = [
    path('order/accept_pending_order/<str:uuid>/', AcceptOrderView.as_view(), name='accept_pending_order'),
    path('order/decline_assigned_order/<str:uuid>/', DeclineAssignedOrderView.as_view()),
    path('order/decline_accepted_order/<str:uuid>/', DeclineAcceptedOrderView.as_view()),
    path('', include(router.urls)),
]