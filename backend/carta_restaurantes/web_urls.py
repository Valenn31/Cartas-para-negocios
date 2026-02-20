from django.urls import path
from . import web_views

urlpatterns = [
    # Debug
    path('debug/', web_views.debug_web_view, name='debug_web_view'),
    
    # Login/Logout
    path('login/', web_views.admin_web_login, name='admin_web_login'),
    path('logout/', web_views.admin_web_logout, name='admin_web_logout'),
    
    # Dashboard
    path('', web_views.admin_web_dashboard, name='admin_web_dashboard'),
    
    # Management Views  
    path('categorias/', web_views.admin_web_categorias, name='admin_web_categorias'),
    path('comidas/', web_views.admin_web_comidas, name='admin_web_comidas'),
    
    # API endpoints for AJAX
    path('api/stats/', web_views.admin_dashboard_stats_api, name='admin_dashboard_stats_api'),
]