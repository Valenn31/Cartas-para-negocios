from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from .models import Categoria, Subcategoria, Comida
from .serializers import CategoriaSerializer, SubcategoriaSerializer, ComidaSerializer

# Vista de login
@api_view(['POST'])
def admin_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if username and password:
        user = authenticate(username=username, password=password)
        if user and user.is_staff:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser
                }
            })
        else:
            return Response({'error': 'Credenciales inválidas o usuario sin permisos de administrador'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
    
    return Response({'error': 'Username y password son requeridos'}, 
                   status=status.HTTP_400_BAD_REQUEST)

# Vista para verificar token
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    if request.user.is_staff:
        return Response({
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'is_staff': request.user.is_staff,
                'is_superuser': request.user.is_superuser
            }
        })
    return Response({'error': 'Usuario sin permisos de administrador'}, 
                   status=status.HTTP_403_FORBIDDEN)

# CRUD para Categorías
class AdminCategoriaList(generics.ListCreateAPIView):
    queryset = Categoria.objects.all().order_by('orden')
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionError("Usuario sin permisos de administrador")
        serializer.save()

class AdminCategoriaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_update(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionError("Usuario sin permisos de administrador")
        serializer.save()
    
    def perform_destroy(self, instance):
        if not self.request.user.is_staff:
            raise PermissionError("Usuario sin permisos de administrador")
        instance.delete()

# CRUD para Subcategorías
class AdminSubcategoriaList(generics.ListCreateAPIView):
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

# CRUD para Comidas
class AdminComidaList(generics.ListCreateAPIView):
    serializer_class = ComidaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        subcategoria_id = self.kwargs.get('subcategoria_id')
        categoria_id = self.kwargs.get('categoria_id')
        
        if subcategoria_id:
            return Comida.objects.filter(subcategoria_id=subcategoria_id)
        elif categoria_id:
            return Comida.objects.filter(categoria_id=categoria_id)
        return Comida.objects.all()
    
    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionError("Usuario sin permisos de administrador")
        serializer.save()

class AdminComidaDetail(generics.RetrieveUpdateDestroyAPIView):
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

# Vista para actualizar orden de categorías
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_categoria_orden(request):
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

# Vista para actualizar orden de subcategorías
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_subcategoria_orden(request):
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
