from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from adminsortable2.admin import SortableAdminMixin
from .models import Restaurante, Categoria, Subcategoria, Comida

# Helper function para obtener el restaurante del usuario
def get_user_restaurant(user):
    """Obtiene el restaurante asociado al usuario logueado"""
    if user.is_superuser:
        return None  # Superuser puede ver todos
    
    # Buscar restaurante donde el usuario es propietario
    try:
        return Restaurante.objects.get(propietario=user)
    except Restaurante.DoesNotExist:
        return None

# Mixin para aplicar tenant isolation
class MultiTenantAdminMixin:
    def get_queryset(self, request):
        """Filtrar queryset por restaurante del usuario"""
        qs = super().get_queryset(request)
        user_restaurant = get_user_restaurant(request.user)
        
        if user_restaurant and hasattr(self.model, 'restaurante'):
            # Filtrar por el restaurante del usuario
            return qs.filter(restaurante=user_restaurant)
        elif request.user.is_superuser:
            # Superuser ve todo
            return qs
        else:
            # Usuario sin restaurante no ve nada
            return qs.none()
    
    def save_model(self, request, obj, form, change):
        """Auto-asignar restaurante al crear/editar"""
        if hasattr(obj, 'restaurante') and not change:  # Solo en creación
            user_restaurant = get_user_restaurant(request.user)
            if user_restaurant:
                obj.restaurante = user_restaurant
        super().save_model(request, obj, form, change)
    
    def get_form(self, request, obj=None, **kwargs):
        """Personalizar formulario según el usuario"""
        form = super().get_form(request, obj, **kwargs)
        user_restaurant = get_user_restaurant(request.user)
        
        # Ocultar campo restaurante para usuarios no-superuser
        if not request.user.is_superuser and 'restaurante' in form.base_fields:
            form.base_fields['restaurante'].widget = admin.widgets.HiddenInput()
        
        return form

@admin.register(Restaurante)
class RestauranteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug', 'propietario', 'activo', 'fecha_creacion']
    list_display_links = ['nombre']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nombre', 'slug', 'propietario__username']
    list_per_page = 50
    readonly_fields = ['fecha_creacion']
    
    def get_queryset(self, request):
        """Solo superusers pueden ver/gestionar restaurantes"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            # Usuarios normales solo ven su propio restaurante
            return qs.filter(propietario=request.user)
    
    def has_add_permission(self, request):
        """Solo superusers pueden agregar restaurantes"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Solo superusers pueden eliminar restaurantes"""
        return request.user.is_superuser

@admin.register(Categoria)
class CategoriaAdmin(MultiTenantAdminMixin, SortableAdminMixin, admin.ModelAdmin):
    list_display = ['nombre', 'imagen', 'restaurante', 'orden']
    list_display_links = ['nombre']
    search_fields = ['nombre']
    list_per_page = 20
    list_filter = ['restaurante'] if admin.ModelAdmin else []
    
    # Solo mostrar restaurante para superusers
    def get_list_display(self, request):
        list_display = ['nombre', 'imagen', 'orden']
        if request.user.is_superuser:
            list_display.insert(2, 'restaurante')
        return list_display
    
    def get_fields(self, request, obj=None):
        fields = ['nombre', 'imagen']
        if request.user.is_superuser:
            fields.append('restaurante')
        return fields
    
    def get_list_filter(self, request):
        if request.user.is_superuser:
            return ['restaurante']
        return []

@admin.register(Subcategoria)
class SubcategoriaAdmin(MultiTenantAdminMixin, SortableAdminMixin, admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'restaurante', 'orden']
    list_display_links = ['nombre']
    list_filter = ['categoria', 'restaurante']
    search_fields = ['nombre', 'categoria__nombre']
    list_per_page = 20
    
    def get_list_display(self, request):
        list_display = ['nombre', 'categoria', 'orden']
        if request.user.is_superuser:
            list_display.insert(2, 'restaurante')
        return list_display
    
    def get_fields(self, request, obj=None):
        fields = ['categoria', 'nombre']
        if request.user.is_superuser:
            fields.append('restaurante')
        return fields
    
    def get_list_filter(self, request):
        if request.user.is_superuser:
            return ['categoria', 'restaurante']
        return ['categoria']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtrar categorías por restaurante del usuario"""
        if db_field.name == "categoria":
            user_restaurant = get_user_restaurant(request.user)
            if user_restaurant:
                kwargs["queryset"] = Categoria.objects.filter(restaurante=user_restaurant)
            elif not request.user.is_superuser:
                kwargs["queryset"] = Categoria.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Comida)
class ComidaAdmin(MultiTenantAdminMixin, admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'subcategoria', 'precio', 'disponible', 'restaurante']
    list_filter = ['categoria', 'subcategoria', 'disponible', 'restaurante']
    list_editable = ['precio', 'disponible']
    search_fields = ['nombre', 'descripcion']
    ordering = ['categoria__orden', 'subcategoria__orden', 'nombre']
    list_per_page = 50
    
    def get_list_display(self, request):
        list_display = ['nombre', 'categoria', 'subcategoria', 'precio', 'disponible']
        if request.user.is_superuser:
            list_display.append('restaurante')
        return list_display
    
    def get_list_filter(self, request):
        if request.user.is_superuser:
            return ['categoria', 'subcategoria', 'disponible', 'restaurante']
        return ['categoria', 'subcategoria', 'disponible']
    
    def get_fields(self, request, obj=None):
        fields = ['categoria', 'subcategoria', 'nombre', 'descripcion', 'precio', 'disponible', 'imagen']
        if request.user.is_superuser:
            fields.append('restaurante')
        return fields
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtrar por restaurante del usuario"""
        user_restaurant = get_user_restaurant(request.user)
        
        if db_field.name == "categoria":
            if user_restaurant:
                kwargs["queryset"] = Categoria.objects.filter(restaurante=user_restaurant)
            elif not request.user.is_superuser:
                kwargs["queryset"] = Categoria.objects.none()
        
        elif db_field.name == "subcategoria":
            if user_restaurant:
                if 'categoria' in request.GET:
                    # Filtrar subcategorías por categoría Y restaurante
                    kwargs["queryset"] = Subcategoria.objects.filter(
                        categoria=request.GET['categoria'],
                        restaurante=user_restaurant
                    )
                else:
                    kwargs["queryset"] = Subcategoria.objects.filter(restaurante=user_restaurant)
            elif not request.user.is_superuser:
                kwargs["queryset"] = Subcategoria.objects.none()
                
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# Customizar el admin site
admin.site.site_header = "Cartas para Negocios - Panel de Administración"
admin.site.site_title = "Admin Cartas"
admin.site.index_title = "Gestión de Restaurantes y Cartas"
