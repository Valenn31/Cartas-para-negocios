from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from .models import Categoria, Subcategoria, Comida

@admin.register(Categoria)
class CategoriaAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['nombre', 'imagen']
    list_display_links = ['nombre']
    search_fields = ['nombre']
    list_per_page = 20
    
    # Solo mostrar los campos que se pueden editar manualmente
    fields = ['nombre', 'imagen']

@admin.register(Subcategoria)
class SubcategoriaAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'orden']
    list_display_links = ['nombre']
    list_filter = ['categoria']
    search_fields = ['nombre', 'categoria__nombre']
    list_per_page = 20
    
    fields = ['categoria', 'nombre']

@admin.register(Comida)
class ComidaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'subcategoria', 'precio', 'disponible']
    list_filter = ['categoria', 'subcategoria', 'disponible']
    list_editable = ['precio', 'disponible']
    search_fields = ['nombre', 'descripcion']
    ordering = ['categoria__orden', 'subcategoria__orden', 'nombre']
    list_per_page = 50
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "subcategoria":
            # Mostrar solo subcategorías de la categoría seleccionada
            if 'categoria' in request.GET:
                kwargs["queryset"] = Subcategoria.objects.filter(categoria=request.GET['categoria'])
            else:
                kwargs["queryset"] = Subcategoria.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
