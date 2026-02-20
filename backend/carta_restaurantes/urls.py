from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.shortcuts import redirect
from carta_restaurantes import web_views

# Vista simple para debug
def debug_view(request):
    return HttpResponse("URLs están funcionando. Ve a /admin/web/login/")

def redirect_to_login(request):
    return redirect('/admin/web/login/')

urlpatterns = [
    path('', redirect_to_login),  # Redireccionar root a login
    
    # URLs web directamente aquí
    path('admin/web/login/', web_views.admin_web_login, name='admin_web_login'),
    path('admin/web/logout/', web_views.admin_web_logout, name='admin_web_logout'),
    path('admin/web/', web_views.admin_web_dashboard, name='admin_web_dashboard'),
    path('admin/web/categorias/', web_views.admin_web_categorias, name='admin_web_categorias'),
    path('admin/web/comidas/', web_views.admin_web_comidas, name='admin_web_comidas'),
    path('admin/web/debug/', web_views.debug_web_view, name='debug_web_view'),
    
    # URLs existentes
    path('admin/', admin.site.urls),
    path('api/', include('carta_restaurantes.api_urls')),
    path('api/admin/', include('carta_restaurantes.admin_urls')),
    path('debug/', debug_view),  # Vista de debug
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
