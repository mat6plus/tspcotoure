from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from cms.admin_site import cms_admin_site

urlpatterns = [
    path('admin/', cms_admin_site.urls),
    path('cms-admin/', include('cms.urls_admin')),
    path('api/', include('cms.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
