from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from .models import Categoria, Comida

@admin.register(Categoria)
class CategoriaAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['nombre', 'imagen']
    list_display_links = ['nombre']
    search_fields = ['nombre']
    list_per_page = 20
    
    # Solo mostrar los campos que se pueden editar manualmente
    fields = ['nombre', 'imagen']

@admin.register(Comida)
class ComidaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio', 'disponible']
    list_filter = ['categoria', 'disponible']
    list_editable = ['precio', 'disponible']
    search_fields = ['nombre', 'descripcion']
    ordering = ['categoria__orden', 'categoria', 'nombre']
    list_per_page = 50
