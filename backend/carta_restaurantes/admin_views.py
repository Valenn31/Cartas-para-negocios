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
        # Superuser ve todos los restaurantes con detalles
        restaurantes = Restaurante.objects.all()
        
        restaurantes_data = []
        total_categorias = 0
        total_subcategorias = 0
        total_comidas = 0
        
        for restaurante in restaurantes:
            categorias_count = Categoria.objects.filter(restaurante=restaurante).count()
            subcategorias_count = Subcategoria.objects.filter(restaurante=restaurante).count()
            comidas_count = Comida.objects.filter(restaurante=restaurante).count()
            
            total_categorias += categorias_count
            total_subcategorias += subcategorias_count
            total_comidas += comidas_count
            
            restaurantes_data.append({
                'id': restaurante.id,
                'nombre': restaurante.nombre,
                'slug': restaurante.slug,
                'descripcion': restaurante.descripcion,
                'propietario': restaurante.propietario.username,
                'estadisticas': {
                    'categorias': categorias_count,
                    'subcategorias': subcategorias_count,
                    'comidas': comidas_count
                },
                'carta_virtual_url': f'https://cartas-para-negocios.vercel.app/?restaurante={restaurante.slug}',
                'admin_url': f'/api/admin/restaurantes/{restaurante.id}/'
            })
        
        return Response({
            'usuario': request.user.username,
            'tipo': 'Super Admin',
            'restaurantes': restaurantes_data,
            'estadisticas_globales': {
                'total_restaurantes': len(restaurantes_data),
                'total_categorias': total_categorias,
                'total_subcategorias': total_subcategorias,
                'total_comidas': total_comidas
            },
            'mensaje': 'Dashboard Super Admin - Todos los restaurantes',
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
    import json
    from urllib.parse import parse_qs, unquote
    
    username = None
    password = None
    
    print(f"DEBUG content_type: {request.content_type}")
    
    # Si el Content-Type está mal pero el contenido es form-data con JSON dentro
    if request.content_type == 'application/x-www-form-urlencoded':
        try:
            # Obtener el body crudo
            body_unicode = request.body.decode('utf-8')
            print(f"DEBUG raw body: '{body_unicode}'")
            
            # Parsear como form-data URL-encoded
            parsed_data = parse_qs(body_unicode)
            print(f"DEBUG parsed form data: {parsed_data}")
            
            # Buscar el campo _content que contiene el JSON
            if '_content' in parsed_data:
                # Extraer y decodificar el JSON del campo _content
                json_content = parsed_data['_content'][0]  # parse_qs devuelve listas
                print(f"DEBUG json_content (URL-encoded): {json_content}")
                
                # Decodificar URL encoding y parsear JSON
                json_decoded = unquote(json_content)
                print(f"DEBUG json_decoded: {json_decoded}")
                
                # Parsear el JSON
                body_data = json.loads(json_decoded)
                print(f"DEBUG body_data: {body_data}")
                
                username = body_data.get('username')
                password = body_data.get('password')
                print(f"DEBUG extracted from _content: username='{username}', password='{password}'")
            else:
                print("DEBUG: No _content field found, trying regular POST data...")
                username = request.POST.get('username')
                password = request.POST.get('password')
                print(f"DEBUG from POST: username='{username}', password='{password}'")
                
        except Exception as e:
            print(f"DEBUG form-data parsing failed: {e}")
            print(f"DEBUG Exception type: {type(e)}")
            # Fallback a métodos normales
            username = request.POST.get('username')
            password = request.POST.get('password')
            print(f"DEBUG fallback to POST: username='{username}', password='{password}'")
    else:
        print("DEBUG: Content-Type is correct, using normal methods...")
        # Content-Type correcto, usar métodos normales
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            print(f"DEBUG from request.data: username='{username}', password='{password}'")
            
            if not username or not password:
                username = request.POST.get('username')
                password = request.POST.get('password')
                print(f"DEBUG fallback to POST: username='{username}', password='{password}'")
        except Exception as e:
            print(f"DEBUG normal parsing failed: {e}")
    
    print(f"DEBUG final: username='{username}', password='{password}'")
    
    if username and password:
        user = authenticate(username=username, password=password)
        print(f"DEBUG authenticate result: {user}")
        
        if user and user.is_staff:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'message': 'Login exitoso! 🎉',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser
                },
                'next_step': 'Ve a /api/admin/ para ver tu dashboard'
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

# Vista simple sin autenticación para testing rápido
@api_view(['GET'])
def simple_dashboard(request):
    """Vista simple para ver datos sin necesidad de token (solo para testing)"""
    
    # Obtener todos los restaurantes
    restaurantes = Restaurante.objects.all()
    
    data = {
        'message': '¡Sistema SaaS Multi-Tenant funcionando! 🎉',
        'total_restaurantes': restaurantes.count(),
        'restaurantes': []
    }
    
    for restaurant in restaurantes:
        categorias = Categoria.objects.filter(restaurante=restaurant)
        comidas = Comida.objects.filter(restaurante=restaurant)
        
        data['restaurantes'].append({
            'nombre': restaurant.nombre,
            'slug': restaurant.slug,
            'propietario': restaurant.propietario.username,
            'stats': {
                'categorias': categorias.count(),
                'comidas': comidas.count()
            },
            'categorias': [
                {
                    'nombre': cat.nombre,
                    'orden': cat.orden
                }
                for cat in categorias.order_by('orden')[:3]  # Solo primeras 3
            ]
        })
    
    return Response(data)

# Vista de test con token por URL (más fácil de probar)
@api_view(['GET'])
def test_dashboard(request):
    """Dashboard con token por parámetro GET (para testing fácil)"""
    
    # Obtener token desde parámetro GET
    token_key = request.GET.get('token')
    
    if not token_key:
        return Response({
            'error': 'Se necesita token',
            'help': 'Agrega ?token=TU_TOKEN a la URL',
            'example': '/api/admin/test/?token=235f3339c92ab97e909d06c24447c7ad12d2c5e2'
        }, status=400)
    
    try:
        # Buscar el token
        token = Token.objects.get(key=token_key)
        user = token.user
        
        # Verificar que sea staff
        if not user.is_staff:
            return Response({'error': 'Usuario sin permisos de administrador'}, status=403)
        
        # Obtener restaurante del usuario
        user_restaurant = get_user_restaurant(user)
        
        if not user_restaurant:
            return Response({
                'error': 'Usuario no tiene restaurante asignado',
                'user': user.username
            }, status=400)
        
        # Obtener datos del restaurante
        categorias = Categoria.objects.filter(restaurante=user_restaurant)
        comidas = Comida.objects.filter(restaurante=user_restaurant)
        
        return Response({
            'success': True,
            'message': f'¡Tenant isolation funcionando! 🎉',
            'user': {
                'username': user.username,
                'email': user.email,
                'is_superuser': user.is_superuser
            },
            'restaurant': {
                'nombre': user_restaurant.nombre,
                'slug': user_restaurant.slug,
                'descripcion': user_restaurant.descripcion
            },
            'stats': {
                'total_categorias': categorias.count(),
                'total_comidas': comidas.count()
            },
            'categorias': [
                {
                    'id': cat.id,
                    'nombre': cat.nombre,
                    'orden': cat.orden
                }
                for cat in categorias.order_by('orden')[:5]  # Solo primeras 5
            ],
            'nota': 'Este usuario solo ve datos de SU restaurante'
        })
        
    except Token.DoesNotExist:
        return Response({
            'error': 'Token inválido',
            'help': 'Haz login primero para obtener un token válido'
        }, status=401)

# Vista para debug - ver todos los tokens
@api_view(['GET'])
def debug_tokens(request):
    """Ver todos los tokens para debug"""
    from rest_framework.authtoken.models import Token
    
    tokens_info = []
    for token in Token.objects.all():
        tokens_info.append({
            'user': token.user.username,
            'key': token.key[:20] + '...',  # Solo primeros 20 chars por seguridad
            'created': token.created,
            'user_is_staff': token.user.is_staff
        })
    
    return Response({
        'message': 'Tokens existentes',
        'count': len(tokens_info),
        'tokens': tokens_info,
        'help': 'Usa uno de estos tokens para probar'
    })

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
