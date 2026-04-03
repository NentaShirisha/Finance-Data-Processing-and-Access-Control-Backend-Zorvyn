"""
Records App URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.records.views import FinancialRecordViewSet

router = DefaultRouter()
router.register(r'', FinancialRecordViewSet, basename='records')

urlpatterns = [
    path('', include(router.urls)),
]
