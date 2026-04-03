"""
URL Configuration for Finance Dashboard Backend.
"""
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # API endpoints
    path('api/auth/', include('apps.users.urls')),
    path('api/records/', include('apps.records.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
