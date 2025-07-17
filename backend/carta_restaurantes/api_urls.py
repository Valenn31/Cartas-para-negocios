from django.urls import path
from . import views

urlpatterns = [
    path('categorias/', views.CategoriaList.as_view()),
    path('categorias/<int:categoria_id>/subcategorias/', views.SubcategoriaList.as_view()),
    path('subcategorias/<int:subcategoria_id>/comidas/', views.ComidaPorSubcategoria.as_view()),
    path('comidas/', views.ComidaList.as_view()),
]
