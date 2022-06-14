from django.urls import path, include

from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.routers import SimpleRouter

from user import views
from user import apis


router = SimpleRouter()
router.register("", views.UserViewSet)

auth_urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", apis.RegistrationView.as_view(), name="registration"),
    path(
        "organization_register/",
        apis.OrganizationRegistrationView.as_view(),
        name="organization_registration",
    ),
    path(
        "team_register/", apis.TeamRegistrationView.as_view(), name="team_registration"
    ),
    path("get_profile/", views.GetUserProfile.as_view(), name="get_profile"),
    path(
        "verify_email/<str:token>/", views.ActivateEmail.as_view(), name="verify_email"
    ),
    path(
        "reset_password/",
        views.SendPasswordResetEmail.as_view(),
        name="reset_password_email",
    ),
    path(
        "verify_reset_password/<str:token>",
        views.VerifyResetPasswordEmail.as_view(),
        name="verify_reset_password",
    ),
    path("change_password/", views.ChangePassword.as_view(), name="change_password"),
]

urlpatterns = [
    path("auth/", include(auth_urlpatterns)),
    path("", include(router.urls)),
]
