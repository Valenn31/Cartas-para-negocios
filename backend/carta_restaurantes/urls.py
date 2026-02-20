from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.shortcuts import redirect

# Vista simple para debug
def debug_view(request):
    return HttpResponse("URLs están funcionando. Ve a /admin/web/login/")

def redirect_to_login(request):
    return redirect('/admin/web/login/')

urlpatterns = [
    path('', redirect_to_login),  # Redireccionar root a login
    path('admin/', admin.site.urls),
    path('api/', include('carta_restaurantes.api_urls')),
    path('api/admin/', include('carta_restaurantes.admin_urls')),
    path('admin/web/', include('carta_restaurantes.web_urls')),
    path('debug/', debug_view),  # Vista de debug
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
