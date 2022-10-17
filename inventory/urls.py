from django.urls import path, include
from rest_framework import routers

from inventory.apis.order import GetOrderByActionView, OrderByActionView
from inventory.views import (
    AcceptOrderView,
    DeclineAcceptedOrderView,
    DeclineAssignedOrderView,
    GetUserAcceptedOrderView,
    GetUserPendingOrderView,
    OrderView,
)
from inventory.apis.product import (
    ProductView,
    VariantFieldView,
    VariantView,
)

router = routers.DefaultRouter()

router.register("product", ProductView)
router.register("variant", VariantView)
router.register("order", OrderView)
router.register("variant_field", VariantFieldView)

order_api_patterns = [
    path("order_action/<uuid:uuid>/<str:action>", OrderByActionView.as_view(), name="order_by_action"),
    path("get_order/<str:action>", GetOrderByActionView.as_view(), name="get_order_by_action"),
]

urlpatterns = [
    path(
        "order/accept_pending_order/<str:uuid>/",
        AcceptOrderView.as_view(),
        name="accept_pending_order",
    ),
    path(
        "order/decline_assigned_order/<str:uuid>/", DeclineAssignedOrderView.as_view()
    ),
    path(
        "order/decline_accepted_order/<str:uuid>/", DeclineAcceptedOrderView.as_view()
    ),
    path("order/get_user_pending_order/", GetUserPendingOrderView.as_view()),
    path("order/get_user_accepted_order/", GetUserAcceptedOrderView.as_view()),
    path("", include(router.urls)),
]+ order_api_patterns
