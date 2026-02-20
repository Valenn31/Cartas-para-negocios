from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Categoria, Subcategoria, Comida, Restaurante

# Helper function para obtener el restaurante del usuario
def get_user_restaurant_view(user):
    """Obtiene el restaurante asociado al usuario logueado"""
    if user.is_superuser:
        return None  # Superuser puede ver todos
    try:
        return Restaurante.objects.get(propietario=user)
    except Restaurante.DoesNotExist:
        return None

# Vista de gestión de categorías usando los templates existentes
@login_required
def manage_categories_view(request):
    """Vista de gestión de categorías usando template existente"""
    user_restaurant = get_user_restaurant_view(request.user)
    
    if not user_restaurant and not request.user.is_superuser:
        return redirect('/admin/web/login/')
    
    # Filtrar categorías por restaurante
    if user_restaurant:
        categorias = Categoria.objects.filter(restaurante=user_restaurant).order_by('orden')
        restaurant_name = user_restaurant.nombre
    else:
        # Superuser ve todas las categorías
        categorias = Categoria.objects.all().order_by('restaurante__nombre', 'orden')
        restaurant_name = "Todas las categorías"
    
    context = {
        'categorias': categorias,
        'user': request.user,
        'restaurant_name': restaurant_name,
        'is_superuser': request.user.is_superuser
    }
    
    return render(request, 'admin/categorias.html', context)

# Vista de gestión de comidas
@login_required  
def manage_foods_view(request):
    """Vista de gestión de comidas por categoría"""
    user_restaurant = get_user_restaurant_view(request.user)
    
    if not user_restaurant and not request.user.is_superuser:
        return redirect('/admin/web/login/')
    
    categoria_id = request.GET.get('categoria')
    
    # Filtrar por restaurante
    if user_restaurant:
        categorias = Categoria.objects.filter(restaurante=user_restaurant).order_by('orden')
        comidas = Comida.objects.filter(restaurante=user_restaurant)
        if categoria_id:
            comidas = comidas.filter(categoria_id=categoria_id)
    else:
        categorias = Categoria.objects.all().order_by('restaurante__nombre', 'orden')
        comidas = Comida.objects.all()
        if categoria_id:
            comidas = comidas.filter(categoria_id=categoria_id)
    
    context = {
        'categorias': categorias,
        'comidas': comidas.order_by('categoria__orden', 'nombre'),
        'selected_categoria': categoria_id,
        'user': request.user,
        'is_superuser': request.user.is_superuser
    }
    
    return render(request, 'admin/comidas.html', context)

# API endpoints para CRUD operations con tenant isolation
@csrf_exempt
@login_required
def api_categories(request):
    """API para gestión de categorías"""
    user_restaurant = get_user_restaurant_view(request.user)
    
    if not user_restaurant and not request.user.is_superuser:
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    if request.method == 'GET':
        if user_restaurant:
            categorias = Categoria.objects.filter(restaurante=user_restaurant)
        else:
            categorias = Categoria.objects.all()
            
        data = [{
            'id': cat.id,
            'nombre': cat.nombre,
            'orden': cat.orden,
            'imagen_url': cat.imagen.url if cat.imagen else None,
            'restaurante': cat.restaurante.nombre
        } for cat in categorias.order_by('orden')]
        
        return JsonResponse(data, safe=False)
    
    elif request.method == 'POST':
        import json
        data = json.loads(request.body)
        
        categoria = Categoria.objects.create(
            nombre=data['nombre'],
            restaurante=user_restaurant or Restaurante.objects.get(id=data['restaurante_id']),
            orden=data.get('orden', 1)
        )
        
        return JsonResponse({
            'id': categoria.id,
            'nombre': categoria.nombre,
            'success': True
        })

# Vista simple para debug
def debug_view(request):
    return HttpResponse("URLs están funcionando. Ve a /admin/web/login/")

def redirect_to_login(request):
    return redirect('/admin/web/login/')

# Vista de login simple directa
def simple_login_view(request):
    html = '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login - Cartas para Negocios</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex; 
                align-items: center; 
                justify-content: center; 
                min-height: 100vh; 
                margin: 0; 
                color: #333;
            }
            .login-card { 
                background: white; 
                padding: 40px; 
                border-radius: 16px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2); 
                width: 100%; 
                max-width: 400px;
            }
            .logo { 
                width: 60px; 
                height: 60px; 
                background: #2563eb; 
                border-radius: 50%; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                margin: 0 auto 20px; 
                color: white; 
                font-size: 24px; 
            }
            h1 { text-align: center; margin-bottom: 30px; color: #1e293b; }
            .form-group { margin-bottom: 20px; }
            label { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-weight: 500; }
            input { width: 100%; padding: 12px; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 16px; }
            input:focus { outline: none; border-color: #2563eb; }
            .login-btn { 
                width: 100%; 
                padding: 14px; 
                background: #2563eb; 
                color: white; 
                border: none; 
                border-radius: 8px; 
                font-size: 16px; 
                cursor: pointer; 
                font-weight: 600;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }
            .login-btn:hover { background: #1d4ed8; }
            .demo-accounts { margin-top: 30px; text-align: center; }
            .demo-accounts h3 { color: #64748b; margin-bottom: 15px; }
            .demo-buttons { display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; }
            .demo-btn { 
                background: #f1f5f9; 
                border: 1px solid #e2e8f0; 
                padding: 8px 12px; 
                border-radius: 8px; 
                cursor: pointer; 
                font-size: 12px;
                display: flex;
                align-items: center;
                gap: 6px;
            }
            .demo-btn:hover { background: #e2e8f0; }
            .alert { 
                padding: 12px; 
                border-radius: 8px; 
                margin-bottom: 20px; 
                display: none; 
            }
            .alert-error { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }
            .alert-success { background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; }
        </style>
    </head>
    <body>
        <div class="login-card">
            <div class="logo">
                <i class="fas fa-utensils"></i>
            </div>
            <h1>Cartas para Negocios</h1>
            
            <div id="alert" class="alert"></div>
            
            <form id="loginForm">
                <div class="form-group">
                    <label><i class="fas fa-user"></i> Usuario</label>
                    <input type="text" id="username" required>
                </div>
                <div class="form-group">
                    <label><i class="fas fa-lock"></i> Contraseña</label>
                    <input type="password" id="password" required>
                </div>
                <button type="submit" class="login-btn">
                    <i class="fas fa-sign-in-alt"></i>
                    Iniciar Sesión
                </button>
            </form>
            
            <div class="demo-accounts">
                <h3>Cuentas de Demostración</h3>
                <div class="demo-buttons">
                    <button class="demo-btn" onclick="fillDemo('admin', 'admin123')">
                        <i class="fas fa-crown"></i> Admin Principal
                    </button>
                    <button class="demo-btn" onclick="fillDemo('restaurante_mario', 'test123')">
                        <i class="fas fa-pizza-slice"></i> Pizzería Mario
                    </button>
                </div>
            </div>
        </div>
        
        <script>
            function fillDemo(user, pass) {
                document.getElementById('username').value = user;
                document.getElementById('password').value = pass;
            }
            
            function showAlert(message, type) {
                const alert = document.getElementById('alert');
                alert.textContent = message;
                alert.className = 'alert alert-' + type;
                alert.style.display = 'block';
            }
            
            document.getElementById('loginForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                
                if (!username || !password) {
                    showAlert('Por favor completa todos los campos', 'error');
                    return;
                }
                
                try {
                    const response = await fetch('/api/admin/auth/login/', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username, password })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        showAlert('¡Login exitoso! Redirigiendo...', 'success');
                        
                        // Determinar el dashboard según el usuario
                        let dashboardUrl;
                        if (username === 'admin') {
                            dashboardUrl = '/admin/web/dashboard/?token=' + data.token;
                        } else {
                            dashboardUrl = '/admin/web/restaurant/?token=' + data.token;
                        }
                        
                        setTimeout(() => {
                            window.location.href = dashboardUrl;
                        }, 1500);
                    } else {
                        showAlert(data.error || 'Error en el login', 'error');
                    }
                } catch (error) {
                    showAlert('Error de conexión', 'error');
                }
            });
        </script>
    </body>
    </html>
    '''
    return HttpResponse(html)

def admin_dashboard_view(request):
    """Dashboard web para super admin con vista de todos los restaurantes"""
    html = '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Dashboard - Cartas para Negocios</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body {
                font-family: 'Montserrat', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            
            .dashboard-container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .header {
                background: white;
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5rem;
                color: #667eea;
                margin-bottom: 10px;
                font-weight: 700;
            }
            
            .header .subtitle {
                color: #666;
                font-size: 1.1rem;
                margin-bottom: 20px;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .stat-card {
                background: white;
                border-radius: 15px;
                padding: 25px;
                text-align: center;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            
            .stat-card:hover {
                transform: translateY(-5px);
            }
            
            .stat-card .icon {
                font-size: 2.5rem;
                color: #667eea;
                margin-bottom: 15px;
            }
            
            .stat-card .number {
                font-size: 2rem;
                font-weight: 700;
                color: #333;
                margin-bottom: 5px;
            }
            
            .stat-card .label {
                color: #666;
                font-weight: 500;
            }
            
            .restaurants-section {
                margin-bottom: 30px;
            }
            
            .section-title {
                color: white;
                font-size: 1.8rem;
                margin-bottom: 20px;
                font-weight: 600;
            }
            
            .restaurants-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                gap: 25px;
            }
            
            .restaurant-card {
                background: white;
                border-radius: 20px;
                padding: 25px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .restaurant-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            }
            
            .restaurant-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, #667eea, #764ba2);
            }
            
            .restaurant-header {
                margin-bottom: 20px;
            }
            
            .restaurant-name {
                font-size: 1.4rem;
                font-weight: 700;
                color: #333;
                margin-bottom: 5px;
            }
            
            .restaurant-owner {
                color: #667eea;
                font-weight: 600;
                font-size: 0.9rem;
            }
            
            .restaurant-description {
                color: #666;
                margin-bottom: 20px;
                font-style: italic;
            }
            
            .restaurant-stats {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin-bottom: 20px;
            }
            
            .mini-stat {
                text-align: center;
                padding: 10px;
                background: #f8f9ff;
                border-radius: 10px;
            }
            
            .mini-stat .mini-number {
                font-size: 1.2rem;
                font-weight: 700;
                color: #667eea;
            }
            
            .mini-stat .mini-label {
                font-size: 0.8rem;
                color: #666;
                margin-top: 2px;
            }
            
            .restaurant-actions {
                display: flex;
                gap: 10px;
            }
            
            .action-btn {
                flex: 1;
                padding: 12px;
                border: none;
                border-radius: 10px;
                font-weight: 600;
                cursor: pointer;
                text-decoration: none;
                text-align: center;
                transition: all 0.3s ease;
                font-size: 0.9rem;
            }
            
            .view-carta-btn {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
            }
            
            .view-carta-btn:hover {
                transform: scale(1.02);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            
            .manage-btn {
                background: #f8f9ff;
                color: #667eea;
                border: 2px solid #667eea;
            }
            
            .manage-btn:hover {
                background: #667eea;
                color: white;
            }
            
            .logout-btn {
                position: fixed;
                top: 20px;
                right: 20px;
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: 2px solid white;
                padding: 10px 20px;
                border-radius: 25px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            
            .logout-btn:hover {
                background: white;
                color: #667eea;
            }
            
            .loading {
                text-align: center;
                padding: 50px;
                color: white;
                font-size: 1.2rem;
            }
            
            .error {
                text-align: center;
                padding: 50px;
                color: #ff6b6b;
                background: white;
                border-radius: 15px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <button class="logout-btn" onclick="logout()">
            <i class="fas fa-sign-out-alt"></i> Cerrar Sesión
        </button>
        
        <div class="dashboard-container">
            <div class="header">
                <h1><i class="fas fa-crown"></i> Dashboard Super Admin</h1>
                <p class="subtitle">Gestiona todos los restaurantes de la plataforma</p>
            </div>
            
            <div id="loading" class="loading">
                <i class="fas fa-spinner fa-spin"></i> Cargando dashboard...
            </div>
            
            <div id="error" class="error" style="display: none;"></div>
            
            <div id="content" style="display: none;">
                <div id="stats-section"></div>
                <div class="restaurants-section">
                    <h2 class="section-title"><i class="fas fa-store"></i> Restaurantes</h2>
                    <div id="restaurants-grid" class="restaurants-grid"></div>
                </div>
            </div>
        </div>
        
        <script>
            // Obtener token de la URL o localStorage
            const urlParams = new URLSearchParams(window.location.search);
            let token = urlParams.get('token') || localStorage.getItem('admin_token');
            
            if (!token) {
                window.location.href = '/admin/web/login/';
                // No usar return fuera de función
            } else {
                // Guardar token en localStorage
                localStorage.setItem('admin_token', token);
                
                // Cargar dashboard al iniciar
                loadDashboard();
            }
            
            async function loadDashboard() {
                try {
                    console.log('Admin Dashboard - Iniciando...');
                    console.log('Admin Dashboard - Token:', token);
                    
                    const url = '/api/admin/test/?token=' + token;
                    console.log('Admin Dashboard - URL:', url);
                    
                    const response = await fetch(url, {
                        method: 'GET'
                    });
                    
                    console.log('Admin Dashboard - Response status:', response.status);
                    console.log('Admin Dashboard - Response ok:', response.ok);
                    
                    if (!response.ok) {
                        const errorText = await response.text();
                        console.error('Admin Dashboard Error Text:', errorText);
                        throw new Error('Error al cargar datos: ' + response.status + ' - ' + errorText);
                    }
                    
                    const data = await response.json();
                    console.log('Admin Dashboard - Data recibida:', data);
                    
                    if (!data || typeof data !== 'object') {
                        throw new Error('Datos inválidos recibidos');
                    }
                    
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('content').style.display = 'block';
                    
                    // Mostrar estadísticas globales
                    if (data.estadisticas_globales) {
                        document.getElementById('stats-section').innerHTML = `
                            <div class="stats-grid">
                                <div class="stat-card">
                                    <div class="icon"><i class="fas fa-store"></i></div>
                                    <div class="number">${data.estadisticas_globales.total_restaurantes}</div>
                                    <div class="label">Restaurantes</div>
                                </div>
                                <div class="stat-card">
                                    <div class="icon"><i class="fas fa-list"></i></div>
                                    <div class="number">${data.estadisticas_globales.total_categorias}</div>
                                    <div class="label">Categorías</div>
                                </div>
                                <div class="stat-card">
                                    <div class="icon"><i class="fas fa-tags"></i></div>
                                    <div class="number">${data.estadisticas_globales.total_subcategorias}</div>
                                    <div class="label">Subcategorías</div>
                                </div>
                                <div class="stat-card">
                                    <div class="icon"><i class="fas fa-utensils"></i></div>
                                    <div class="number">${data.estadisticas_globales.total_comidas}</div>
                                    <div class="label">Comidas</div>
                                </div>
                            </div>
                        `;
                    }
                    
                    // Mostrar restaurantes
                    if (data.restaurantes) {
                        const restaurantsHTML = data.restaurantes.map(restaurant => `
                            <div class="restaurant-card">
                                <div class="restaurant-header">
                                    <h3 class="restaurant-name">${restaurant.nombre}</h3>
                                    <p class="restaurant-owner">
                                        <i class="fas fa-user"></i> ${restaurant.propietario}
                                    </p>
                                </div>
                                <p class="restaurant-description">${restaurant.descripcion}</p>
                                <div class="restaurant-stats">
                                    <div class="mini-stat">
                                        <div class="mini-number">${restaurant.estadisticas.categorias}</div>
                                        <div class="mini-label">Categorías</div>
                                    </div>
                                    <div class="mini-stat">
                                        <div class="mini-number">${restaurant.estadisticas.subcategorias}</div>
                                        <div class="mini-label">Subcategorías</div>
                                    </div>
                                    <div class="mini-stat">
                                        <div class="mini-number">${restaurant.estadisticas.comidas}</div>
                                        <div class="mini-label">Comidas</div>
                                    </div>
                                </div>
                                <div class="restaurant-actions">
                                    <a href="${restaurant.carta_virtual_url}" target="_blank" class="action-btn view-carta-btn">
                                        <i class="fas fa-external-link-alt"></i> Ver Carta
                                    </a>
                                    <a href="/admin/manage/categories/" class="action-btn manage-btn">
                                        <i class="fas fa-cog"></i> Gestionar
                                    </a>
                                </div>
                            </div>
                        `).join('');
                        
                        document.getElementById('restaurants-grid').innerHTML = restaurantsHTML;
                    }
                    
                } catch (error) {
                    console.error('Admin Dashboard - Error completo:', error);
                    console.error('Admin Dashboard - Error stack:', error.stack);
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('error').style.display = 'block';
                    document.getElementById('error').innerHTML = `
                        <h3>Error Admin Dashboard:</h3>
                        <p><strong>Mensaje:</strong> ${error.message}</p>
                        <p><strong>Token:</strong> ${token ? token.substring(0, 20) + '...' : 'No token'}</p>
                        <p><strong>URL:</strong> /api/admin/test/?token=...</p>
                        <p>Revisa la consola (F12) para más detalles.</p>
                    `;
                }
            }
            
            function manageRestaurant(slug) {
                alert(`Funcionalidad de gestión para ${slug} - Próximamente disponible`);
            }
            
            function logout() {
                localStorage.removeItem('admin_token');
                window.location.href = '/admin/web/login/';
            }
        </script>
    </body>
    </html>
    '''
    return HttpResponse(html)

def restaurant_dashboard_view(request):
    """Dashboard web para dueños de restaurante específico"""
    html = '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard Restaurante - Cartas para Negocios</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body {
                font-family: 'Montserrat', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            
            .dashboard-container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .header {
                background: white;
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                text-align: center;
                position: relative;
            }
            
            .restaurant-info h1 {
                font-size: 2.2rem;
                color: #667eea;
                margin-bottom: 10px;
                font-weight: 700;
            }
            
            .restaurant-info .subtitle {
                color: #666;
                font-size: 1.1rem;
                margin-bottom: 20px;
            }
            
            .view-carta-main {
                display: inline-block;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 15px 30px;
                border-radius: 25px;
                text-decoration: none;
                font-weight: 600;
                transition: all 0.3s ease;
                margin-top: 15px;
            }
            
            .view-carta-main:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .stat-card {
                background: white;
                border-radius: 15px;
                padding: 25px;
                text-align: center;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            
            .stat-card:hover {
                transform: translateY(-5px);
            }
            
            .stat-card .icon {
                font-size: 2.5rem;
                color: #667eea;
                margin-bottom: 15px;
            }
            
            .stat-card .number {
                font-size: 2rem;
                font-weight: 700;
                color: #333;
                margin-bottom: 5px;
            }
            
            .stat-card .label {
                color: #666;
                font-weight: 500;
            }
            
            .actions-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
            }
            
            .action-card {
                background: white;
                border-radius: 15px;
                padding: 25px;
                text-align: center;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
                cursor: pointer;
                text-decoration: none;
                color: #333;
                display: block;
            }
            
            a.action-card,
            a.action-card:visited,
            a.action-card:link {
                color: #333;
                text-decoration: none;
            }
            
            .action-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0,0,0,0.15);
            }
            
            .action-card .icon {
                font-size: 2.5rem;
                color: #667eea;
                margin-bottom: 15px;
            }
            
            .action-card h3 {
                color: #333;
                margin-bottom: 10px;
                font-weight: 600;
            }
            
            .action-card p {
                color: #666;
                font-size: 0.9rem;
            }
            
            .logout-btn {
                position: fixed;
                top: 20px;
                right: 20px;
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: 2px solid white;
                padding: 10px 20px;
                border-radius: 25px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            
            .logout-btn:hover {
                background: white;
                color: #667eea;
            }
            
            .loading, .error {
                text-align: center;
                padding: 50px;
                color: white;
                font-size: 1.2rem;
            }
            
            .error {
                background: rgba(255, 107, 107, 0.2);
                border-radius: 15px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <button class="logout-btn" onclick="logout()">
            <i class="fas fa-sign-out-alt"></i> Cerrar Sesión
        </button>
        
        <div class="dashboard-container">
            <div id="loading" class="loading">
                <i class="fas fa-spinner fa-spin"></i> Cargando dashboard...
            </div>
            
            <div id="error" class="error" style="display: none;"></div>
            
            <div id="content" style="display: none;">
                <div class="header">
                    <div class="restaurant-info">
                        <h1 id="restaurant-name"><i class="fas fa-store"></i> Mi Restaurante</h1>
                        <p class="subtitle" id="restaurant-description">Panel de control de tu restaurante</p>
                        <a id="view-carta-link" href="#" target="_blank" class="view-carta-main">
                            <i class="fas fa-external-link-alt"></i> Ver Mi Carta Virtual
                        </a>
                    </div>
                </div>
                
                <div id="stats-section" class="stats-grid"></div>
                
                <div class="actions-grid">
                    <a href="/admin/manage/categories/" class="action-card">
                        <div class="icon"><i class="fas fa-list"></i></div>
                        <h3>Gestionar Categorías</h3>
                        <p>Organiza y edita las categorías de tu menú</p>
                    </a>
                    <a href="/admin/manage/foods/" class="action-card">
                        <div class="icon"><i class="fas fa-utensils"></i></div>
                        <h3>Gestionar Comidas</h3>
                        <p>Añade, edita o elimina platos de tu carta</p>
                    </a>
                    <div class="action-card" onclick="viewStats()">
                        <div class="icon"><i class="fas fa-chart-bar"></i></div>
                        <h3>Estadísticas</h3>
                        <p>Ve el rendimiento y métricas de tu restaurante</p>
                    </div>
                    <div class="action-card" onclick="settings()">
                        <div class="icon"><i class="fas fa-cog"></i></div>
                        <h3>Configuración</h3>
                        <p>Ajusta la configuración de tu restaurante</p>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Obtener token de la URL o localStorage
            const urlParams = new URLSearchParams(window.location.search);
            let token = urlParams.get('token') || localStorage.getItem('admin_token');
            
            if (!token) {
                window.location.href = '/admin/web/login/';
                // No usar return fuera de función
            } else {
                // Guardar token en localStorage
                localStorage.setItem('admin_token', token);
                
                // Cargar dashboard al iniciar
                loadDashboard();
            }
            
            async function loadDashboard() {
                try {
                    console.log('Restaurant Dashboard - Iniciando...');
                    console.log('Restaurant Dashboard - Token:', token);
                    console.log('Restaurant Dashboard - Enviando request a /api/admin/test/');
                    
                    const url = '/api/admin/test/?token=' + token;
                    console.log('Restaurant Dashboard - URL completa:', url);
                    
                    const response = await fetch(url, {
                        method: 'GET'
                    });
                    
                    console.log('Restaurant Dashboard - Response status:', response.status);
                    console.log('Restaurant Dashboard - Response ok:', response.ok);
                    
                    if (!response.ok) {
                        const errorText = await response.text();
                        console.error('Restaurant Dashboard Error response:', errorText);
                        throw new Error('Error al cargar datos: ' + response.status + ' - ' + errorText);
                    }
                    
                    const data = await response.json();
                    console.log('Restaurant Dashboard - Data recibida:', data);
                    
                    if (data.tipo === 'Super Admin') {
                        // Si es super admin, redirigir al dashboard de admin
                        window.location.href = '/admin/web/dashboard/?token=' + token;
                        return;
                    }
                    
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('content').style.display = 'block';
                    
                    // Actualizar información del restaurante
                    document.getElementById('restaurant-name').innerHTML = '<i class="fas fa-store"></i> ' + data.restaurante;
                    document.getElementById('restaurant-description').textContent = 'Panel de control de ' + data.restaurante;
                    document.getElementById('view-carta-link').href = `https://cartas-para-negocios.vercel.app/?restaurante=${data.slug}`;
                    
                    // Mostrar estadísticas
                    if (data.estadisticas) {
                        document.getElementById('stats-section').innerHTML = `
                            <div class="stat-card">
                                <div class="icon"><i class="fas fa-list"></i></div>
                                <div class="number">${data.estadisticas.categorias}</div>
                                <div class="label">Categorías</div>
                            </div>
                            <div class="stat-card">
                                <div class="icon"><i class="fas fa-tags"></i></div>
                                <div class="number">${data.estadisticas.subcategorias || 0}</div>
                                <div class="label">Subcategorías</div>
                            </div>
                            <div class="stat-card">
                                <div class="icon"><i class="fas fa-utensils"></i></div>
                                <div class="number">${data.estadisticas.comidas}</div>
                                <div class="label">Comidas</div>
                            </div>
                        `;
                    }
                    
                } catch (error) {
                    console.error('Restaurant Dashboard - Error completo:', error);
                    console.error('Restaurant Dashboard - Error stack:', error.stack);
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('error').style.display = 'block';
                    document.getElementById('error').innerHTML = `
                        <h3>Error Restaurant Dashboard:</h3>
                        <p><strong>Mensaje:</strong> ${error.message}</p>
                        <p><strong>Token:</strong> ${token ? token.substring(0, 20) + '...' : 'No token'}</p>
                        <p><strong>URL:</strong> /api/admin/test/?token=...</p>
                        <p>Revisa la consola (F12) para más detalles.</p>
                    `;
                }
            }
            
            function manageCategories() {
                alert('Gestión de categorías - Próximamente disponible');
            }
            
            function manageComidas() {
                alert('Gestión de comidas - Próximamente disponible');
            }
            
            function viewStats() {
                alert('Estadísticas avanzadas - Próximamente disponible');
            }
            
            function settings() {
                alert('Configuración - Próximamente disponible');
            }
            
            function logout() {
                localStorage.removeItem('admin_token');
                window.location.href = '/admin/web/login/';
            }
        </script>
    </body>
    </html>
    '''
    return HttpResponse(html)

urlpatterns = [
    path('', redirect_to_login),
    
    # Vista de login simple que funciona
    path('admin/web/login/', simple_login_view, name='simple_login'),
    
    # Dashboard web para admin
    path('admin/web/dashboard/', admin_dashboard_view, name='admin_dashboard'),
    
    # Dashboard web para restaurante individual
    path('admin/web/restaurant/', restaurant_dashboard_view, name='restaurant_dashboard'),
    
    # Vistas de gestión con templates existentes
    path('admin/manage/categories/', manage_categories_view, name='manage_categories'),
    path('admin/manage/foods/', manage_foods_view, name='manage_foods'),
    
    # API endpoints para gestión
    path('api/categories/', api_categories, name='api_categories'),
    
    # URLs existentes que sabemos que funcionan
    path('admin/', admin.site.urls),
    path('api/', include('carta_restaurantes.api_urls')),
    path('api/admin/', include('carta_restaurantes.admin_urls')),
    path('debug/', debug_view),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
