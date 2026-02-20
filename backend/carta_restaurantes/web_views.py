from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.authtoken.models import Token
from .models import Restaurante, Categoria, Comida
from .admin_views import get_user_restaurant
import json

@csrf_exempt
@require_http_methods(["GET", "POST"])
def admin_web_login(request):
    """Vista web para login del admin"""
    if request.user.is_authenticated:
        return redirect('admin_web_dashboard')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            if username and password:
                user = authenticate(username=username, password=password)
                if user and user.is_staff:
                    login(request, user)
                    token, created = Token.objects.get_or_create(user=user)
                    return JsonResponse({
                        'success': True,
                        'message': 'Login exitoso',
                        'token': token.key,
                        'redirect_url': '/admin/web/'
                    })
                else:
                    return JsonResponse({
                        'error': 'Credenciales inválidas o usuario sin permisos'
                    }, status=401)
            else:
                return JsonResponse({
                    'error': 'Username y password son requeridos'
                }, status=400)
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Datos JSON inválidos'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'error': f'Error interno: {str(e)}'
            }, status=500)
    
    return render(request, 'admin/login.html')

@login_required
def admin_web_dashboard(request):
    """Vista web del dashboard principal"""
    user_restaurant = get_user_restaurant(request.user)
    
    if not user_restaurant:
        messages.error(request, 'Usuario no tiene restaurante asignado')
        return redirect('admin_web_login')
    
    # Obtener estadísticas
    categorias = Categoria.objects.filter(restaurante=user_restaurant)
    comidas = Comida.objects.filter(restaurante=user_restaurant)
    
    # Calcular precio promedio
    precios = comidas.values_list('precio', flat=True)
    promedio_precio = sum(precios) / len(precios) if precios else 0
    
    # Categorías con conteo de comidas
    categorias_con_stats = []
    for categoria in categorias.order_by('orden')[:6]:  # Solo primeras 6
        comidas_count = comidas.filter(categoria=categoria).count()
        categorias_con_stats.append({
            'id': categoria.id,
            'nombre': categoria.nombre,
            'orden': categoria.orden,
            'imagen': categoria.imagen,
            'comidas_count': comidas_count
        })
    
    context = {
        'restaurant': user_restaurant,
        'stats': {
            'total_categorias': categorias.count(),
            'total_comidas': comidas.count(),
            'promedio_precio': round(promedio_precio, 2)
        },
        'categorias': categorias_con_stats
    }
    
    return render(request, 'admin/dashboard.html', context)

@login_required
def admin_web_categorias(request):
    """Vista web para gestión de categorías"""
    user_restaurant = get_user_restaurant(request.user)
    
    if not user_restaurant:
        messages.error(request, 'Usuario no tiene restaurante asignado')
        return redirect('admin_web_login')
    
    categorias = Categoria.objects.filter(restaurante=user_restaurant).order_by('orden')
    
    context = {
        'restaurant': user_restaurant,
        'categorias': categorias
    }
    
    return render(request, 'admin/categorias.html', context)

@login_required
def admin_web_comidas(request):
    """Vista web para gestión de comidas"""
    user_restaurant = get_user_restaurant(request.user)
    
    if not user_restaurant:
        messages.error(request, 'Usuario no tiene restaurante asignado')
        return redirect('admin_web_login')
    
    comidas = Comida.objects.filter(restaurante=user_restaurant).select_related('categoria')
    categorias = Categoria.objects.filter(restaurante=user_restaurant).order_by('orden')
    
    context = {
        'restaurant': user_restaurant,
        'comidas': comidas,
        'categorias': categorias
    }
    
    return render(request, 'admin/comidas.html', context)

def admin_web_logout(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('admin_web_login')

@login_required
def admin_dashboard_stats_api(request):
    """API para obtener stats actualizadas del dashboard"""
    user_restaurant = get_user_restaurant(request.user)
    
    if not user_restaurant:
        return JsonResponse({'error': 'Usuario no tiene restaurante asignado'}, status=400)
    
    categorias = Categoria.objects.filter(restaurante=user_restaurant)
    comidas = Comida.objects.filter(restaurante=user_restaurant)
    
    # Calcular precio promedio
    precios = comidas.values_list('precio', flat=True)
    promedio_precio = sum(precios) / len(precios) if precios else 0
    
    return JsonResponse({
        'stats': {
            'total_categorias': categorias.count(),
            'total_comidas': comidas.count(),
            'promedio_precio': round(promedio_precio, 2)
        }
    })