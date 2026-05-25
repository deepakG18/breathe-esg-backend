from django.urls import path
from .views import SAPUploadView, DashboardView, UtilityUploadView, TravelUploadView, ActivityApproveView, ActivityFixView

urlpatterns = [
    path('api/upload/sap/', SAPUploadView.as_view(), name='sap-upload'),
    path('api/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('api/upload/utility/', UtilityUploadView.as_view(), name='utility-upload'),
    path('api/upload/travel/', TravelUploadView.as_view(), name='travel-upload'),
    path('api/approve/<int:pk>/', ActivityApproveView.as_view(), name='approve-record'),
    path('api/fix/<int:pk>/', ActivityFixView.as_view(), name='fix-record'),
]