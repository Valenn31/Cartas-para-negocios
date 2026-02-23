"""
Admin Debug - Endpoints de debug y desarrollo (SOLO PARA settings.DEBUG=True)
"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Categoria, Subcategoria, Comida, Restaurante
from .admin_helpers import get_user_restaurant


@api_view(['GET'])
def setup_test_users(request):
    """
    Crear usuarios de prueba con credenciales conocidas.
    
    SOLO PARA DESARROLLO - Este endpoint debe estar protegido con settings.DEBUG
    en admin_urls.py
    """
    try:
        # Crear/actualizar super admin (ve TODOS los restaurantes)
        superadmin_user, created = User.objects.get_or_create(
            username='superadmin',
            defaults={'email': 'superadmin@test.com', 'is_staff': True, 'is_superuser': True}
        )
        superadmin_user.is_staff = True
        superadmin_user.is_superuser = True
        superadmin_user.set_password('admin123')
        superadmin_user.save()
        
        # Crear/actualizar usuario admin (dueño del restaurante principal)
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@test.com', 'is_staff': True}
        )
        admin_user.set_password('123123')
        admin_user.is_staff = True
        admin_user.is_superuser = False
        admin_user.save()
        
        # Crear/actualizar usuario restaurante test
        mario_user, created = User.objects.get_or_create(
            username='restaurante_mario',
            defaults={'email': 'mario@test.com', 'is_staff': True}
        )
        mario_user.is_staff = True
        mario_user.set_password('test123')
        mario_user.save()
        
        # Crear restaurante por defecto para admin si no existe
        admin_restaurant, created = Restaurante.objects.get_or_create(
            slug='restaurante-principal',
            defaults={
                'nombre': 'Restaurante Principal',
                'descripcion': 'Restaurante del administrador',
                'propietario': admin_user
            }
        )
        if not created:
            admin_restaurant.propietario = admin_user
            admin_restaurant.save()
        
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
                'superadmin': {
                    'username': 'superadmin',
                    'password': 'admin123',
                    'tipo': 'Super Admin - Ve TODOS los restaurantes',
                    'funcionalidad': 'Dashboard global, estadísticas combinadas'
                },
                'admin': {
                    'username': 'admin',
                    'password': '123123',
                    'tipo': 'Propietario - Solo ve SU restaurante',
                    'restaurante': admin_restaurant.nombre
                },
                'restaurante_mario': {
                    'username': 'restaurante_mario', 
                    'password': 'test123',
                    'tipo': 'Propietario - Solo ve SU restaurante',
                    'restaurante': mario_restaurant.nombre
                }
            },
            'sistema_configurado': {
                'super_admin': 'superadmin - Ve dashboard global con TODOS los restaurantes',
                'propietarios': 'admin y restaurante_mario - Solo ven SUS restaurantes específicos',
                'separacion_completa': 'Cada propietario edita SOLO su menú'
            },
            'next_step': 'Ahora puedes hacer login en /api/admin/auth/login/ con estas credenciales'
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def debug_current_user(request):
    """Debug helper para ver qué usuario está usando el dashboard."""
    token_key = request.GET.get('token')
    
    if not token_key:
        return Response({
            'error': 'Se necesita token',
            'help': 'Agrega ?token=TU_TOKEN a la URL'
        }, status=400)
    
    try:
        token = Token.objects.get(key=token_key)
        user = token.user
        user_restaurant = get_user_restaurant(user)
        
        user_info = {
            'username': user.username,
            'email': user.email,
            'is_superuser': user.is_superuser,
            'is_staff': user.is_staff,
            'is_active': user.is_active,
            'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        restaurant_info = None
        if user_restaurant:
            restaurant_info = {
                'id': user_restaurant.id,
                'nombre': user_restaurant.nombre,
                'slug': user_restaurant.slug,
                'descripcion': user_restaurant.descripcion,
                'activo': user_restaurant.activo
            }
        
        stats_info = {}
        if user_restaurant:
            stats_info = {
                'categorias': Categoria.objects.filter(restaurante=user_restaurant).count(),
                'subcategorias': Subcategoria.objects.filter(restaurante=user_restaurant).count(),
                'comidas': Comida.objects.filter(restaurante=user_restaurant).count(),
                'tipo_vista': 'Propietario de Restaurante - Solo su restaurante'
            }
        elif user.is_superuser:
            total_categorias = Categoria.objects.count()
            total_subcategorias = Subcategoria.objects.count()
            total_comidas = Comida.objects.count()
            stats_info = {
                'categorias': total_categorias,
                'subcategorias': total_subcategorias, 
                'comidas': total_comidas,
                'tipo_vista': 'Super Admin - Todos los restaurantes (ESTADÍSTICAS GLOBALES)'
            }
        
        return Response({
            'usuario_actual': user_info,
            'restaurante_asignado': restaurant_info,
            'estadisticas_que_ve': stats_info,
            'problema_detectado': 'Estás usando SUPERUSER (admin) en lugar de PROPIETARIO (restaurante_mario)' if user.is_superuser else 'Usuario correcto',
            'solucion': 'Haz logout y login con: usuario=restaurante_mario, password=test123' if user.is_superuser else 'Todo correcto'
        })
        
    except Token.DoesNotExist:
        return Response({'error': 'Token inválido'}, status=401)


@api_view(['GET'])
def debug_real_data(request):
    """Debug completo: muestra EXACTAMENTE qué hay en la BD para cada restaurante."""
    token_key = request.GET.get('token')
    
    if not token_key:
        return Response({
            'error': 'Se necesita token',
            'help': 'Agrega ?token=TU_TOKEN a la URL'
        }, status=400)
    
    try:
        token = Token.objects.get(key=token_key)
        user = token.user
        
        if not user.is_staff:
            return Response({'error': 'Usuario sin permisos de administrador'}, status=403)
        
        restaurantes = Restaurante.objects.all()
        
        restaurantes_detalle = []
        for restaurante in restaurantes:
            categorias = Categoria.objects.filter(restaurante=restaurante).order_by('orden')
            categorias_detalle = []
            
            for categoria in categorias:
                subcategorias = Subcategoria.objects.filter(categoria=categoria).order_by('orden')
                subcategorias_detalle = []
                
                for subcategoria in subcategorias:
                    comidas = Comida.objects.filter(restaurante=restaurante, subcategoria=subcategoria).order_by('orden')
                    comidas_detalle = [{'id': c.id, 'nombre': c.nombre, 'precio': str(c.precio)} for c in comidas]
                    
                    subcategorias_detalle.append({
                        'id': subcategoria.id,
                        'nombre': subcategoria.nombre,
                        'orden': subcategoria.orden,
                        'comidas_count': len(comidas_detalle),
                        'comidas': comidas_detalle
                    })
                
                categorias_detalle.append({
                    'id': categoria.id,
                    'nombre': categoria.nombre,
                    'orden': categoria.orden,
                    'imagen': categoria.imagen.url if categoria.imagen else None,
                    'subcategorias_count': len(subcategorias_detalle),
                    'subcategorias': subcategorias_detalle
                })
            
            total_categorias = len(categorias_detalle)
            total_subcategorias = sum(len(cat['subcategorias']) for cat in categorias_detalle)
            total_comidas = Comida.objects.filter(restaurante=restaurante).count()
            
            restaurantes_detalle.append({
                'id': restaurante.id,
                'nombre': restaurante.nombre,
                'slug': restaurante.slug,
                'propietario': restaurante.propietario.username,
                'conteos': {
                    'categorias': total_categorias,
                    'subcategorias': total_subcategorias,
                    'comidas': total_comidas
                },
                'contenido_completo': {
                    'categorias': categorias_detalle
                }
            })
        
        return Response({
            'usuario_consultando': user.username,
            'timestamp': timezone.now(),
            'restaurantes_completos': restaurantes_detalle,
            'mensaje': 'Contenido COMPLETO y REAL de la base de datos',
            'nota': 'Compara estos números con lo que ves en el dashboard'
        })
        
    except Token.DoesNotExist:
        return Response({'error': 'Token inválido'}, status=401)


@api_view(['GET'])
def debug_tokens(request):
    """Ver todos los tokens para debug."""
    tokens_info = []
    for token in Token.objects.all():
        tokens_info.append({
            'user': token.user.username,
            'key': token.key[:20] + '...',
            'created': token.created,
            'user_is_staff': token.user.is_staff
        })
    
    return Response({
        'message': 'Tokens existentes',
        'count': len(tokens_info),
        'tokens': tokens_info,
        'help': 'Usa uno de estos tokens para probar'
    })
