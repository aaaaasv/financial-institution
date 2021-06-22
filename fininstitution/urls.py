from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from rest_framework.schemas import get_schema_view

urlpatterns = [
    path('openapi/', get_schema_view(
        title="Financial Institution API",
        description="API for financial institution",
        version="1.0.0",
        urlconf='accounts.urls'
    ), name='openapi-schema'),
    path('', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger-ui'),
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
]
