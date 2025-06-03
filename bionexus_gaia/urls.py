"""
URL configuration for bionexus_gaia project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/v1/biodiversity/', include('bionexus_gaia.apps.biodiversity.urls')),
    path('api/v1/ai/', include('bionexus_gaia.apps.ai.urls')),
    path('api/v1/citizen/', include('bionexus_gaia.apps.citizen.urls')),
    path('api/v1/auth/', include('bionexus_gaia.apps.users.auth_urls')),
    path('api/v1/users/', include('bionexus_gaia.apps.users.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
