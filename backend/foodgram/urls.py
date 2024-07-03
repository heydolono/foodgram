from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from recipes.views import redirect_short_link

urlpatterns = [
    path('s/<str:short_link>/', redirect_short_link, name='short_link_redirect'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/', include('users.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 