from django.urls import path
from . import admin_views

urlpatterns = [
    # Autenticación
    path('auth/login/', admin_views.admin_login, name='admin_login'),
    path('auth/verify/', admin_views.verify_token, name='verify_token'),
    
    # Gestión de Categorías
    path('categorias/', admin_views.AdminCategoriaList.as_view(), name='admin_categorias'),
    path('categorias/<int:pk>/', admin_views.AdminCategoriaDetail.as_view(), name='admin_categoria_detail'),
    path('categorias/orden/', admin_views.update_categoria_orden, name='update_categoria_orden'),
    
    # Gestión de Subcategorías
    path('subcategorias/', admin_views.AdminSubcategoriaList.as_view(), name='admin_subcategorias'),
    path('categorias/<int:categoria_id>/subcategorias/', admin_views.AdminSubcategoriaList.as_view(), name='admin_subcategorias_by_categoria'),
    path('subcategorias/<int:pk>/', admin_views.AdminSubcategoriaDetail.as_view(), name='admin_subcategoria_detail'),
    path('subcategorias/orden/', admin_views.update_subcategoria_orden, name='update_subcategoria_orden'),
    
    # Gestión de Comidas
    path('comidas/', admin_views.AdminComidaList.as_view(), name='admin_comidas'),
    path('categorias/<int:categoria_id>/comidas/', admin_views.AdminComidaList.as_view(), name='admin_comidas_by_categoria'),
    path('subcategorias/<int:subcategoria_id>/comidas/', admin_views.AdminComidaList.as_view(), name='admin_comidas_by_subcategoria'),
    path('comidas/<int:pk>/', admin_views.AdminComidaDetail.as_view(), name='admin_comida_detail'),
]
