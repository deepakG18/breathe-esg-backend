from django.urls import path
from .views import SAPUploadView, DashboardView, UtilityUploadView, TravelUploadView, ActivityApproveView, ActivityFixView, SetupDataView, ResetPasswordView

urlpatterns = [
    path('api/upload/sap/', SAPUploadView.as_view(), name='sap-upload'),
    path('api/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('api/upload/utility/', UtilityUploadView.as_view(), name='utility-upload'),
    path('api/upload/travel/', TravelUploadView.as_view(), name='travel-upload'),
    path('api/approve/<int:pk>/', ActivityApproveView.as_view(), name='approve-record'),
    path('api/fix/<int:pk>/', ActivityFixView.as_view(), name='fix-record'),
    path('api/setup/', SetupDataView.as_view(), name='setup-data'),
    path('api/reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]