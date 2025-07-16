from django.urls import path
from . import views

urlpatterns = [
    path('categorias/', views.CategoriaList.as_view()),
    path('comidas/', views.ComidaList.as_view()),
]
