"""
User App URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users.views import AuthViewSet, UserViewSet, RoleViewSet

router = DefaultRouter()
router.register(r'', AuthViewSet, basename='auth')
router.register(r'users', UserViewSet, basename='users')
router.register(r'roles', RoleViewSet, basename='roles')

urlpatterns = [
    path('', include(router.urls)),
]
