from rest_framework import generics
from django.shortcuts import get_object_or_404
from .models import Categoria, Subcategoria, Comida, Restaurante
from .serializers import CategoriaSerializer, SubcategoriaSerializer, ComidaSerializer

class CategoriaList(generics.ListAPIView):
    serializer_class = CategoriaSerializer
    
    def get_queryset(self):
        # CORREGIDO: Filtrar por restaurante desde parámetro GET
        restaurante_slug = self.request.GET.get('restaurante')
        
        if not restaurante_slug:
            # Si no hay parámetro, devolver vacío (seguridad)
            return Categoria.objects.none()
        
        # Obtener restaurante por slug
        restaurante = get_object_or_404(Restaurante, slug=restaurante_slug, activo=True)
        
        # Solo categorías de ESE restaurante
        return Categoria.objects.filter(restaurante=restaurante).order_by('orden')

class SubcategoriaList(generics.ListAPIView):
    serializer_class = SubcategoriaSerializer
    
    def get_queryset(self):
        categoria_id = self.kwargs.get('categoria_id')
        restaurante_slug = self.request.GET.get('restaurante')
        
        if not restaurante_slug:
            return Subcategoria.objects.none()
            
        # Verificar que la categoría pertenece al restaurante correcto
        restaurante = get_object_or_404(Restaurante, slug=restaurante_slug, activo=True)
        categoria = get_object_or_404(Categoria, id=categoria_id, restaurante=restaurante)
        
        return Subcategoria.objects.filter(categoria=categoria).order_by('orden')

class ComidaList(generics.ListAPIView):
    serializer_class = ComidaSerializer
    
    def get_queryset(self):
        # CORREGIDO: Filtrar por restaurante desde parámetro GET
        restaurante_slug = self.request.GET.get('restaurante')
        
        if not restaurante_slug:
            return Comida.objects.none()
        
        restaurante = get_object_or_404(Restaurante, slug=restaurante_slug, activo=True)
        return Comida.objects.filter(restaurante=restaurante)

class ComidaPorSubcategoria(generics.ListAPIView):
    serializer_class = ComidaSerializer
    
    def get_queryset(self):
        subcategoria_id = self.kwargs.get('subcategoria_id')
        restaurante_slug = self.request.GET.get('restaurante')
        
        if not restaurante_slug:
            return Comida.objects.none()
            
        # Verificar que la subcategoría pertenece al restaurante correcto
        restaurante = get_object_or_404(Restaurante, slug=restaurante_slug, activo=True)
        
        return Comida.objects.filter(
            subcategoria_id=subcategoria_id,
            restaurante=restaurante,
            disponible=True
        )
