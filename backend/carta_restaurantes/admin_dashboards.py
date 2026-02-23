"""
Admin Dashboards - Vistas de dashboard para diferentes tipos de usuarios
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import Categoria, Subcategoria, Comida, Restaurante
from .admin_helpers import get_user_restaurant


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard(request):
    """
    Dashboard principal para usuarios autenticados.
    
    - Propietarios: Ven solo su restaurante y sus estadísticas
    - Superadmin: Ve todos los restaurantes con estadísticas globales
    """
    user_restaurant = get_user_restaurant(request.user)
    
    if user_restaurant:
        # Usuario propietario de restaurante
        categorias = Categoria.objects.filter(restaurante=user_restaurant).count()
        categorias_del_restaurante = Categoria.objects.filter(restaurante=user_restaurant)
        subcategorias = Subcategoria.objects.filter(categoria__in=categorias_del_restaurante).count()
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
        # Superuser: dashboard global
        restaurantes = Restaurante.objects.all()
        
        restaurantes_data = []
        total_categorias = 0
        total_subcategorias = 0
        total_comidas = 0
        
        for restaurante in restaurantes:
            categorias_count = Categoria.objects.filter(restaurante=restaurante).count()
            categorias_del_restaurante = Categoria.objects.filter(restaurante=restaurante)
            subcategorias_count = Subcategoria.objects.filter(categoria__in=categorias_del_restaurante).count()
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


@api_view(['GET'])
def simple_dashboard(request):
    """Vista simple sin autenticación para testing rápido."""
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
                {'nombre': cat.nombre, 'orden': cat.orden}
                for cat in categorias.order_by('orden')[:3]
            ]
        })
    
    return Response(data)


@api_view(['GET'])
def test_dashboard(request):
    """Dashboard con token por parámetro GET para testing fácil."""
    token_key = request.GET.get('token')
    
    if not token_key:
        return Response({
            'error': 'Se necesita token',
            'help': 'Agrega ?token=TU_TOKEN a la URL',
            'example': '/api/admin/test/?token=235f3339c92ab97e909d06c24447c7ad12d2c5e2'
        }, status=400)
    
    try:
        token = Token.objects.get(key=token_key)
        user = token.user
        
        if not user.is_staff:
            return Response({'error': 'Usuario sin permisos de administrador'}, status=403)
        
        user_restaurant = get_user_restaurant(user)
        
        if user_restaurant:
            categorias = Categoria.objects.filter(restaurante=user_restaurant).count()
            categorias_del_restaurante = Categoria.objects.filter(restaurante=user_restaurant)
            subcategorias = Subcategoria.objects.filter(categoria__in=categorias_del_restaurante).count()
            comidas = Comida.objects.filter(restaurante=user_restaurant).count()
            
            return Response({
                'usuario': user.username,
                'restaurante': user_restaurant.nombre,
                'slug': user_restaurant.slug,
                'estadisticas': {
                    'categorias': categorias,
                    'subcategorias': subcategorias,
                    'comidas': comidas
                },
                'mensaje': f'Tenant isolation funcionando! Solo ves datos de {user_restaurant.nombre}.',
                'urls_disponibles': {
                    'categorias': '/api/admin/categorias/',
                    'subcategorias': '/api/admin/subcategorias/',
                    'comidas': '/api/admin/comidas/'
                }
            })
            
        elif user.is_superuser:
            restaurantes = Restaurante.objects.all()
            
            restaurantes_data = []
            total_categorias = 0
            total_subcategorias = 0
            total_comidas = 0
            
            for restaurante in restaurantes:
                categorias_count = Categoria.objects.filter(restaurante=restaurante).count()
                categorias_del_restaurante = Categoria.objects.filter(restaurante=restaurante)
                subcategorias_count = Subcategoria.objects.filter(categoria__in=categorias_del_restaurante).count()
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
                'usuario': user.username,
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
                'usuario': user.username,
                'error': 'Usuario sin restaurante asignado',
                'mensaje': 'Contacta al administrador para asignar un restaurante'
            }, status=403)
            
    except Token.DoesNotExist:
        return Response({
            'error': 'Token inválido',
            'help': 'Haz login primero para obtener un token válido'
        }, status=401)
