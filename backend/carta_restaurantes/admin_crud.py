"""
Admin CRUD - Vistas CRUD para Categorías, Subcategorías y Comidas
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from .models import Categoria, Subcategoria, Comida
from.serializers import CategoriaSerializer, SubcategoriaSerializer, ComidaSerializer
from .admin_helpers import get_user_restaurant


# ============================================================================
# CRUD - CATEGORÍAS
# ============================================================================

class AdminCategoriaList(generics.ListCreateAPIView):
    """Lista y creación de categorías con aislamiento multi-tenant."""
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_restaurant = get_user_restaurant(self.request.user)
        if user_restaurant:
            return Categoria.objects.filter(restaurante=user_restaurant).order_by('orden')
        elif self.request.user.is_superuser:
            return Categoria.objects.all().order_by('orden')
        else:
            return Categoria.objects.none()
    
    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionError("Usuario sin permisos de administrador")
        
        user_restaurant = get_user_restaurant(self.request.user)
        if user_restaurant:
            serializer.save(restaurante=user_restaurant)
        elif self.request.user.is_superuser:
            serializer.save()
        else:
            raise PermissionError("Usuario sin restaurante asignado")


class AdminCategoriaDetail(generics.RetrieveUpdateDestroyAPIView):
    """Detalle, actualización y eliminación de categorías."""
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_restaurant = get_user_restaurant(self.request.user)
        if user_restaurant:
            return Categoria.objects.filter(restaurante=user_restaurant)
        elif self.request.user.is_superuser:
            return Categoria.objects.all()
        else:
            return Categoria.objects.none()
    
    def perform_update(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionError("Usuario sin permisos de administrador")
        serializer.save()
    
    def perform_destroy(self, instance):
        if not self.request.user.is_staff:
            raise PermissionError("Usuario sin permisos de administrador")
        instance.delete()


# ============================================================================
# CRUD - SUBCATEGORÍAS
# ============================================================================

class AdminSubcategoriaList(generics.ListCreateAPIView):
    """Lista y creación de subcategorías."""
    serializer_class = SubcategoriaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        categoria_id = self.kwargs.get('categoria_id')
        if categoria_id:
            return Subcategoria.objects.filter(categoria_id=categoria_id).order_by('orden')
        return Subcategoria.objects.all().order_by('categoria__orden', 'orden')
    
    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionError("Usuario sin permisos de administrador")
        serializer.save()


class AdminSubcategoriaDetail(generics.RetrieveUpdateDestroyAPIView):
    """Detalle, actualización y eliminación de subcategorías."""
    queryset = Subcategoria.objects.all()
    serializer_class = SubcategoriaSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_update(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionError("Usuario sin permisos de administrador")
        serializer.save()
    
    def perform_destroy(self, instance):
        if not self.request.user.is_staff:
            raise PermissionError("Usuario sin permisos de administrador")
        instance.delete()


# ============================================================================
# CRUD - COMIDAS
# ============================================================================

class AdminComidaList(generics.ListCreateAPIView):
    """Lista y creación de comidas."""
    serializer_class = ComidaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        subcategoria_id = self.kwargs.get('subcategoria_id')
        categoria_id = self.kwargs.get('categoria_id')
        
        if subcategoria_id:
            return Comida.objects.filter(subcategoria_id=subcategoria_id).order_by('orden')
        elif categoria_id:
            return Comida.objects.filter(categoria_id=categoria_id).order_by('orden')
        return Comida.objects.all().order_by('orden')
    
    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionError("Usuario sin permisos de administrador")
        serializer.save()


class AdminComidaDetail(generics.RetrieveUpdateDestroyAPIView):
    """Detalle, actualización y eliminación de comidas."""
    queryset = Comida.objects.all()
    serializer_class = ComidaSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_update(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionError("Usuario sin permisos de administrador")
        serializer.save()
    
    def perform_destroy(self, instance):
        if not self.request.user.is_staff:
            raise PermissionError("Usuario sin permisos de administrador")
        instance.delete()


# ============================================================================
# REORDENAMIENTO
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_categoria_orden(request):
    """Actualiza el orden de múltiples categorías en una transacción atómica."""
    if not request.user.is_staff:
        return Response({'error': 'Usuario sin permisos de administrador'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    categoria_orders = request.data.get('orders', [])
    
    try:
        with transaction.atomic():
            for item in categoria_orders:
                categoria_id = item.get('id')
                nuevo_orden = item.get('orden')
                if categoria_id and nuevo_orden is not None:
                    Categoria.objects.filter(id=categoria_id).update(orden=nuevo_orden)
        
        return Response({'message': 'Orden actualizado correctamente'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_subcategoria_orden(request):
    """Actualiza el orden de múltiples subcategorías en una transacción atómica."""
    if not request.user.is_staff:
        return Response({'error': 'Usuario sin permisos de administrador'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    subcategoria_orders = request.data.get('orders', [])
    
    try:
        with transaction.atomic():
            for item in subcategoria_orders:
                subcategoria_id = item.get('id')
                nuevo_orden = item.get('orden')
                if subcategoria_id and nuevo_orden is not None:
                    Subcategoria.objects.filter(id=subcategoria_id).update(orden=nuevo_orden)
        
        return Response({'message': 'Orden actualizado correctamente'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_comida_orden(request):
    """Actualiza el orden de múltiples comidas en una transacción atómica."""
    if not request.user.is_staff:
        return Response({'error': 'Usuario sin permisos de administrador'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    comida_orders = request.data.get('orders', [])
    
    try:
        with transaction.atomic():
            for item in comida_orders:
                comida_id = item.get('id')
                nuevo_orden = item.get('orden')
                if comida_id and nuevo_orden is not None:
                    Comida.objects.filter(id=comida_id).update(orden=nuevo_orden)
        
        return Response({'message': 'Orden actualizado correctamente'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
