from django.urls import include, path
from rest_framework.routers import DefaultRouter


from users.apps import UsersConfig

from .views import UserViewSet

app_name = UsersConfig.name


router = DefaultRouter()
router.register(r"users", UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # path("register/", RegisterView.as_view(), name="register"),
    # path(
    #     "login/",
    #     TokenObtainPairView.as_view(permission_classes=(AllowAny,)),
    #     name="login",
    # ),
    # path(
    #     "token/refresh/",
    #     TokenRefreshView.as_view(permission_classes=(AllowAny,)),
    #     name="token_refresh",
    # ),
]
