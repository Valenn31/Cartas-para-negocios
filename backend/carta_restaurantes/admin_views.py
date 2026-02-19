from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Categoria, Subcategoria, Comida, Restaurante
from .serializers import CategoriaSerializer, SubcategoriaSerializer, ComidaSerializer

# Función helper para obtener el restaurante del usuario
def get_user_restaurant(user):
    """Obtiene el restaurante asociado al usuario logueado"""
    if user.is_superuser:
        # Superuser puede ver todos, devolvemos None para indicarlo
        return None
    
    # Buscar restaurante donde el usuario es propietario
    try:
        return Restaurante.objects.get(propietario=user, activo=True)
    except Restaurante.DoesNotExist:
        # Si no tiene restaurante, crear uno temporal o lanzar error
        return None

# Endpoint temporal para crear usuarios de prueba
@api_view(['GET'])
def setup_test_users(request):
    """Crear usuarios de prueba con credenciales conocidas - SOLO PARA DESARROLLO"""
    
    try:
        # Crear/actualizar usuario admin
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@test.com', 'is_staff': True, 'is_superuser': True}
        )
        admin_user.set_password('admin123')
        admin_user.save()
        
        # Crear/actualizar usuario restaurante test
        mario_user, created = User.objects.get_or_create(
            username='restaurante_mario',
            defaults={'email': 'mario@test.com', 'is_staff': True}
        )
        mario_user.set_password('test123')
        mario_user.save()
        
        # Crear restaurante por defecto para admin si no existe
        admin_restaurant, created = Restaurante.objects.get_or_create(
            slug='restaurante-principal',
            defaults={
                'nombre': 'Restaurante Principal',
                'descripcion': 'Restaurante original',
                'propietario': admin_user
            }
        )
        
        # Crear restaurante para mario
        mario_restaurant, created = Restaurante.objects.get_or_create(
            slug='pizzeria-mario',
            defaults={
                'nombre': 'Pizzería Mario',
                'descripcion': 'Restaurante de prueba',
                'propietario': mario_user
            }
        )
        
        return Response({
            'message': 'Usuarios de prueba creados exitosamente',
            'usuarios': {
                'admin': {
                    'username': 'admin',
                    'password': 'admin123',
                    'tipo': 'Super Admin',
                    'restaurante': admin_restaurant.nombre
                },
                'restaurante_mario': {
                    'username': 'restaurante_mario', 
                    'password': 'test123',
                    'tipo': 'Dueño de Restaurante',
                    'restaurante': mario_restaurant.nombre
                }
            },
            'next_step': 'Ahora puedes hacer login en /api/admin/auth/login/ con estas credenciales'
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

# Vista de dashboard de prueba
@api_view(['GET'])
def admin_dashboard(request):
    """Dashboard simple para probar multi-tenant"""
    
    if not request.user.is_authenticated:
        return Response({
            'message': 'No autenticado. Haz login primero en /api/admin/auth/login/',
            'login_url': '/api/admin/auth/login/',
            'test_users': {
                'admin': 'password_admin',
                'restaurante_mario': 'test123'
            }
        }, status=401)
    
    user_restaurant = get_user_restaurant(request.user)
    
    if user_restaurant:
        # Usuario con restaurante
        categorias = Categoria.objects.filter(restaurante=user_restaurant).count()
        subcategorias = Subcategoria.objects.filter(restaurante=user_restaurant).count()
        comidas = Comida.objects.filter(restaurante=user_restaurant).count()
        
        return Response({
            'usuario': request.user.username,
            'restaurante': user_restaurant.nombre,
            'slug': user_restaurant.slug,
            'estadisticas': {
                'categorias': categorias,
                'subcategorias': subcategorias,
                'comidas': comidas
            },
            'mensaje': f'Bienvenido a {user_restaurant.nombre}! Solo ves datos de tu restaurante.',
            'urls_disponibles': {
                'categorias': '/api/admin/categorias/',
                'subcategorias': '/api/admin/subcategorias/',
                'comidas': '/api/admin/comidas/'
            }
        })
        
    elif request.user.is_superuser:
        # Superuser ve todo
        categorias = Categoria.objects.all().count()
        subcategorias = Subcategoria.objects.all().count()
        comidas = Comida.objects.all().count()
        restaurantes = Restaurante.objects.all().count()
        
        return Response({
            'usuario': request.user.username,
            'tipo': 'Super Admin',
            'estadisticas_globales': {
                'restaurantes': restaurantes,
                'categorias': categorias,
                'subcategorias': subcategorias,
                'comidas': comidas
            },
            'mensaje': 'Eres super admin! Ves todos los datos de todos los restaurantes.',
            'urls_disponibles': {
                'categorias': '/api/admin/categorias/',
                'subcategorias': '/api/admin/subcategorias/',
                'comidas': '/api/admin/comidas/'
            }
        })
    else:
        return Response({
            'usuario': request.user.username,
            'error': 'Usuario sin restaurante asignado',
            'mensaje': 'Contacta al administrador para asignar un restaurante'
        }, status=403)

# Vista de login
@api_view(['POST'])
def admin_login(request):
    # Manejar tanto JSON como form-data
    username = None
    password = None
    
    # Intentar obtener de request.data (JSON/DRF)
    if request.data:
        username = request.data.get('username')
        password = request.data.get('password')
    
    # Si no funcionó, intentar desde POST (form-data)
    if not username or not password:
        username = request.POST.get('username')
        password = request.POST.get('password')
    
    # DEBUG
    print(f"DEBUG username: '{username}', password: '{password}'")
    print(f"DEBUG content_type: {request.content_type}")
    
    if username and password:
        user = authenticate(username=username, password=password)
        print(f"DEBUG authenticate result: {user}")
        
        if user and user.is_staff:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'message': 'Login exitoso',
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
    
    return Response({
        'error': 'Username y password son requeridos',
        'debug_info': {
            'content_type': request.content_type,
            'username_received': bool(username),
            'password_received': bool(password)
        }
    }, status=status.HTTP_400_BAD_REQUEST)

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
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_restaurant = get_user_restaurant(self.request.user)
        if user_restaurant:
            # Usuario normal: solo sus categorías
            return Categoria.objects.filter(restaurante=user_restaurant).order_by('orden')
        elif self.request.user.is_superuser:
            # Superuser: todas las categorías
            return Categoria.objects.all().order_by('orden')
        else:
            # Usuario sin restaurante: ninguna categoría
            return Categoria.objects.none()
    
    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionError("Usuario sin permisos de administrador")
        
        user_restaurant = get_user_restaurant(self.request.user)
        if user_restaurant:
            # Asignar automáticamente el restaurante del usuario
            serializer.save(restaurante=user_restaurant)
        elif self.request.user.is_superuser:
            # Superuser debe especificar el restaurante manualmente
            serializer.save()
        else:
            raise PermissionError("Usuario sin restaurante asignado")

class AdminCategoriaDetail(generics.RetrieveUpdateDestroyAPIView):
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
            return Comida.objects.filter(subcategoria_id=subcategoria_id).order_by('orden')
        elif categoria_id:
            return Comida.objects.filter(categoria_id=categoria_id).order_by('orden')
        return Comida.objects.all().order_by('orden')
    
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


# Vista para actualizar orden de comidas
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_comida_orden(request):
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
