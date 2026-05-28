from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_home(request):
    return JsonResponse({
        "status": "Live",
        "message": "Welcome to the Breathe ESG Backend API",
        "documentation": "Please refer to the GitHub repository for API endpoints and architecture."
    })

urlpatterns = [
    path('', api_home, name='home'),
    path('admin/', admin.site.urls),
    path('', include('esg_core.urls')), 
]