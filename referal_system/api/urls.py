from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from api.views import AuthViewSet, UserViewSet

router = DefaultRouter()

router.register('users', UserViewSet)
router.register('auth', AuthViewSet, basename='auth')
urlpatterns = [
    path('', include(router.urls)),
    path('token/refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),
]
