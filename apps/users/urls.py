from django.urls import re_path, include, path
from .serializers import VerifyTokenSerializer
from .views import (
    LoginView,
    UserSignUp,
    UpdatePassword,
    LogoutView,
    DeleteTokens,
    UserList,
    UpdateUser,
    DeleteUser,
    UserStatus, EmailChecker, UserRolesListView,
)
# router = routers.DefaultRouter()
# router.register(r"users", UserViewSet)
# Builtin Views for token management of simplejwt
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # built-in Urls of simplejwt
    re_path(r"^refresh/token/", TokenRefreshView.as_view(), name="token_refresh"),
    re_path(r"^token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    re_path(
        r"^verify/token",
        TokenVerifyView.as_view(serializer_class=VerifyTokenSerializer),
        name="token_verify",
    ),
    # re_path(r"^", include(router.urls)),
    re_path(r"^auth/", include("rest_auth.urls")),
    # Custom urls User management
    re_path(r"^login/", LoginView.as_view(), name="login_view"),
    re_path(r"^logout/", LogoutView.as_view(), name="logout_view"),
    re_path(r"^delete-tokens/", DeleteTokens.as_view(), name="delete-tokens"),
    re_path(r"^signup/", UserSignUp.as_view(), name="signup_view"),
    re_path(r"^update-pass/", UpdatePassword.as_view(), name="update_pass"),
    re_path(r"^all-users/", UserList.as_view(), name="all_users"),
    path("update-user/<int:user_id>/", UpdateUser.as_view(), name="update_user"),
    path("delete-user/<int:user_id>/", DeleteUser.as_view(), name="delete_user"),
    path("user-status/<int:user_id>/", UserStatus.as_view(), name="user_status"),
    path("user-roles/", UserRolesListView.as_view(), name="user_roles"),
    path("email-checker/", EmailChecker.as_view(), name="email_checker")
]
