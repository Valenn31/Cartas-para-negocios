from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from .models import Categoria, Subcategoria, Comida, Restaurante
from functools import wraps
import json

# Decorador personalizado para login
def custom_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/admin/web/login/')
        return view_func(request, *args, **kwargs)
    return wrapper

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
@custom_login_required
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
@custom_login_required
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

# Vista de editor por restaurante específico
@custom_login_required
def restaurant_editor_view(request, slug):
    """Editor completo para un restaurante específico"""
    # Obtener el restaurante
    try:
        restaurante = Restaurante.objects.get(slug=slug)
    except Restaurante.DoesNotExist:
        return redirect('/admin/web/login/')
    
    # Verificar permiso: solo superuser o propietario del restaurante
    user_restaurant = get_user_restaurant_view(request.user)
    if not request.user.is_superuser and user_restaurant != restaurante:
        return redirect('/admin/web/login/')
    
    # Obtener datos del restaurante
    categorias = Categoria.objects.filter(restaurante=restaurante).order_by('orden')
    subcategorias = Subcategoria.objects.filter(restaurante=restaurante).order_by('orden')
    comidas = Comida.objects.filter(restaurante=restaurante).order_by('categoria__orden', 'orden')
    
    context = {
        'restaurante': restaurante,
        'categorias': categorias,
        'subcategorias': subcategorias,
        'comidas': comidas,
        'user': request.user,
        'is_superuser': request.user.is_superuser
    }
    
    return render(request, 'admin/restaurant_editor.html', context)

# API endpoints para CRUD operations con tenant isolation
@csrf_exempt
def api_categories(request):
    """API para gestión de categorías"""
    # Verificar autenticación manualmente
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'}, status=401)
        
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
    return render(request, 'admin/login.html')

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
            
            /* Modal de crear restaurante */
            .modal-overlay {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.7);
                z-index: 2000;
                justify-content: center;
                align-items: center;
            }
            
            .modal-overlay.show {
                display: flex;
            }
            
            .modal-content {
                background: white;
                border-radius: 15px;
                padding: 40px;
                width: 90%;
                max-width: 500px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            }
            
            .modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
                padding-bottom: 15px;
                border-bottom: 2px solid #667eea;
            }
            
            .modal-header h2 {
                color: #667eea;
                font-size: 1.5rem;
                margin: 0;
            }
            
            .modal-close {
                background: none;
                border: none;
                font-size: 28px;
                color: #999;
                cursor: pointer;
                padding: 0;
                width: 30px;
                height: 30px;
            }
            
            .modal-close:hover {
                color: #333;
            }
            
            .form-group {
                margin-bottom: 20px;
            }
            
            .form-group label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #333;
                font-size: 0.95rem;
            }
            
            .form-group input,
            .form-group select,
            .form-group textarea {
                width: 100%;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 1rem;
                font-family: inherit;
            }
            
            .form-group textarea {
                resize: vertical;
                min-height: 80px;
            }
            
            .form-group input:focus,
            .form-group select:focus,
            .form-group textarea:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            
            .modal-footer {
                display: flex;
                gap: 10px;
                margin-top: 30px;
            }
            
            .btn-modal {
                flex: 1;
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .btn-create {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            
            .btn-create:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            
            .btn-create:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            
            .btn-cancel {
                background: #f0f0f0;
                color: #333;
            }
            
            .btn-cancel:hover {
                background: #e0e0e0;
            }
            
            .btn-new-restaurant {
                background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                margin-bottom: 30px;
                transition: all 0.3s ease;
                display: inline-flex;
                align-items: center;
                gap: 8px;
            }
            
            .btn-new-restaurant:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(81, 207, 102, 0.4);
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
                    <button class="btn-new-restaurant" onclick="openModalCrearRestaurante()">
                        <i class="fas fa-plus"></i> Nuevo Restaurante
                    </button>
                    <h2 class="section-title"><i class="fas fa-store"></i> Restaurantes</h2>
                    <div id="restaurants-grid" class="restaurants-grid"></div>
                </div>
            </div>
            
            <!-- Modal para crear restaurante -->
            <div id="modal-crear-restaurante" class="modal-overlay">
                <div class="modal-content">
                    <div class="modal-header">
                        <h2><i class="fas fa-store"></i> Crear Nuevo Restaurante</h2>
                        <button class="modal-close" onclick="closeModalCrearRestaurante()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <form id="form-crear-restaurante" onsubmit="handleCrearRestaurante(event)">
                        <div class="form-group">
                            <label for="input-nombre-restaurante">Nombre del Restaurante *</label>
                            <input type="text" id="input-nombre-restaurante" name="nombre" required placeholder="Ej: Restaurante Mario">
                        </div>
                        <div class="form-group">
                            <label for="input-descripcion-restaurante">Descripción</label>
                            <textarea id="input-descripcion-restaurante" name="descripcion" placeholder="Descripción del restaurante..."></textarea>
                        </div>
                        <div class="form-group">
                            <label for="input-username-cliente">Usuario (Username) *</label>
                            <input type="text" id="input-username-cliente" name="username" required placeholder="Ej: cliente123">
                        </div>
                        <div class="form-group">
                            <label for="input-email-cliente">Email *</label>
                            <input type="email" id="input-email-cliente" name="email" required placeholder="Ej: cliente@example.com">
                        </div>
                        <div class="form-group">
                            <label for="input-password-cliente">Contraseña *</label>
                            <input type="password" id="input-password-cliente" name="password" required placeholder="Mínimo 8 caracteres">
                        </div>
                        <div class="form-group">
                            <label for="input-password-confirm">Confirmar Contraseña *</label>
                            <input type="password" id="input-password-confirm" name="password_confirm" required placeholder="Repite la contraseña">
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn-modal btn-cancel" onclick="closeModalCrearRestaurante()">
                                <i class="fas fa-times"></i> Cancelar
                            </button>
                            <button type="submit" class="btn-modal btn-create">
                                <i class="fas fa-check"></i> Crear Restaurante
                            </button>
                        </div>
                    </form>
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
            
            // Funciones para crear restaurante
            async function openModalCrearRestaurante() {
                // Mostrar modal
                document.getElementById('modal-crear-restaurante').classList.add('show');
                // Limpiar formulario
                document.getElementById('form-crear-restaurante').reset();
            }
            
            function closeModalCrearRestaurante() {
                document.getElementById('modal-crear-restaurante').classList.remove('show');
            }
            
            async function handleCrearRestaurante(event) {
                event.preventDefault();
                
                const nombre = document.getElementById('input-nombre-restaurante').value;
                const descripcion = document.getElementById('input-descripcion-restaurante').value;
                const username = document.getElementById('input-username-cliente').value;
                const email = document.getElementById('input-email-cliente').value;
                const password = document.getElementById('input-password-cliente').value;
                const passwordConfirm = document.getElementById('input-password-confirm').value;
                const btnSubmit = document.querySelector('#form-crear-restaurante button[type="submit"]');
                const originalText = btnSubmit.innerHTML;
                
                // Validar contraseñas
                if (password !== passwordConfirm) {
                    alert('Las contraseñas no coinciden');
                    return;
                }
                
                if (password.length < 8) {
                    alert('La contraseña debe tener al menos 8 caracteres');
                    return;
                }
                
                btnSubmit.disabled = true;
                btnSubmit.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creando...';
                
                try {
                    const response = await fetch('/admin/restaurante/create/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({
                            nombre: nombre,
                            descripcion: descripcion,
                            username: username,
                            email: email,
                            password: password
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        btnSubmit.innerHTML = '<i class="fas fa-check"></i> ¡Creado!';
                        btnSubmit.style.backgroundColor = '#51cf66';
                        
                        setTimeout(() => {
                            closeModalCrearRestaurante();
                            loadDashboard();
                            btnSubmit.disabled = false;
                            btnSubmit.innerHTML = originalText;
                            btnSubmit.style.backgroundColor = '';
                        }, 1500);
                    } else {
                        btnSubmit.disabled = false;
                        btnSubmit.innerHTML = '<i class="fas fa-times"></i> Error';
                        btnSubmit.style.backgroundColor = '#ff6b6b';
                        alert('Error: ' + (data.error || 'No se pudo crear'));
                        
                        setTimeout(() => {
                            btnSubmit.innerHTML = originalText;
                            btnSubmit.style.backgroundColor = '';
                        }, 2000);
                    }
                } catch (error) {
                    console.error('Error:', error);
                    btnSubmit.disabled = false;
                    btnSubmit.innerHTML = '<i class="fas fa-times"></i> Error';
                    btnSubmit.style.backgroundColor = '#ff6b6b';
                    
                    setTimeout(() => {
                        btnSubmit.innerHTML = originalText;
                        btnSubmit.style.backgroundColor = '';
                    }, 2000);
                }
            }
            
            function getCookie(name) {
                let cookieValue = null;
                if (document.cookie && document.cookie !== '') {
                    const cookies = document.cookie.split(';');
                    for (let i = 0; i < cookies.length; i++) {
                        const cookie = cookies[i].trim();
                        if (cookie.substring(0, name.length + 1) === (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            
            // Cerrar modal al clickear fuera
            window.onclick = function(event) {
                const modal = document.getElementById('modal-crear-restaurante');
                if (event.target === modal) {
                    closeModalCrearRestaurante();
                }
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
            
            .action-card.featured {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: 3px solid #fff;
                box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
            }
            
            .action-card.featured:hover {
                transform: translateY(-8px);
                box-shadow: 0 20px 40px rgba(102, 126, 234, 0.4);
            }
            
            .action-card.featured .icon {
                color: #fff;
                font-size: 3rem;
            }
            
            .action-card.featured h3,
            .action-card.featured p {
                color: white;
            }
            
            .action-card.featured h3 {
                font-weight: 700;
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
                    <a href="javascript:openEditor()" class="action-card featured">
                        <div class="icon"><i class="fas fa-edit"></i></div>
                        <h3>Editor Completo</h3>
                        <p>Editor avanzado con drag & drop y todas las funciones</p>
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
            let restauranteSlug = null;  // Variable global para guardar el slug del restaurante
            
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
                    
                    // Guardar el slug del restaurante para usarlo en el editor
                    restauranteSlug = data.slug;
                    
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
            
            function openEditor() {
                // Redirigir al editor específico del restaurante
                if (!restauranteSlug) {
                    alert('Error: No se pudo obtener el restaurante');
                    return;
                }
                window.location.href = `/admin/web/restaurant/${restauranteSlug}/editor/`;
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

@custom_login_required
@csrf_exempt
def update_categoria(request, categoria_id):
    """API para actualizar una categoría"""
    try:
        categoria = Categoria.objects.get(id=categoria_id)
        user_restaurant = get_user_restaurant_view(request.user)
        
        # Verificar permisos
        if not request.user.is_superuser and user_restaurant != categoria.restaurante:
            return JsonResponse({'success': False, 'error': 'No tienes permiso'}, status=403)
        
        if request.method == 'POST':
            data = json.loads(request.body)
            categoria.nombre = data.get('nombre', categoria.nombre)
            categoria.orden = data.get('orden', categoria.orden)
            categoria.save()
            return JsonResponse({'success': True, 'message': 'Categoría actualizada'})
    except Categoria.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Categoría no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@custom_login_required
@csrf_exempt
def delete_categoria(request, categoria_id):
    """API para eliminar una categoría"""
    try:
        categoria = Categoria.objects.get(id=categoria_id)
        user_restaurant = get_user_restaurant_view(request.user)
        
        # Verificar permisos
        if not request.user.is_superuser and user_restaurant != categoria.restaurante:
            return JsonResponse({'success': False, 'error': 'No tienes permiso'}, status=403)
        
        if request.method == 'POST':
            categoria.delete()
            return JsonResponse({'success': True, 'message': 'Categoría eliminada'})
    except Categoria.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Categoría no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@custom_login_required
@csrf_exempt
def update_comida(request, comida_id):
    """API para actualizar una comida"""
    try:
        comida = Comida.objects.get(id=comida_id)
        user_restaurant = get_user_restaurant_view(request.user)
        
        # Verificar permisos
        if not request.user.is_superuser and user_restaurant != comida.categoria.restaurante:
            return JsonResponse({'success': False, 'error': 'No tienes permiso'}, status=403)
        
        if request.method == 'POST':
            data = json.loads(request.body)
            comida.nombre = data.get('nombre', comida.nombre)
            comida.descripcion = data.get('descripcion', comida.descripcion)
            comida.precio = data.get('precio', comida.precio)
            comida.disponible = data.get('disponible', comida.disponible)
            comida.save()
            return JsonResponse({'success': True, 'message': 'Comida actualizada'})
    except Comida.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Comida no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@custom_login_required
@csrf_exempt
def delete_comida(request, comida_id):
    """API para eliminar una comida"""
    try:
        comida = Comida.objects.get(id=comida_id)
        user_restaurant = get_user_restaurant_view(request.user)
        
        # Verificar permisos
        if not request.user.is_superuser and user_restaurant != comida.categoria.restaurante:
            return JsonResponse({'success': False, 'error': 'No tienes permiso'}, status=403)
        
        if request.method == 'POST':
            comida.delete()
            return JsonResponse({'success': True, 'message': 'Comida eliminada'})
    except Comida.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Comida no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@custom_login_required
def get_propietarios(request):
    """API para obtener lista de propietarios disponibles - Solo superadmin"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Solo superadmin'}, status=403)
    
    # Obtener usuarios que no sean superuser
    propietarios = User.objects.filter(is_superuser=False).values('id', 'username', 'email')
    
    return JsonResponse({
        'success': True,
        'propietarios': list(propietarios)
    })

@custom_login_required
@csrf_exempt
def create_restaurante(request):
    """API para crear un nuevo restaurante con usuario - Solo superadmin"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Solo superadmin puede crear restaurantes'}, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validar campos requeridos
            nombre = data.get('nombre', '').strip()
            descripcion = data.get('descripcion', '').strip()
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '').strip()
            
            if not nombre:
                return JsonResponse({'success': False, 'error': 'El nombre del restaurante es requerido'}, status=400)
            
            if not username:
                return JsonResponse({'success': False, 'error': 'El nombre de usuario es requerido'}, status=400)
            
            if not email:
                return JsonResponse({'success': False, 'error': 'El email es requerido'}, status=400)
            
            if not password:
                return JsonResponse({'success': False, 'error': 'La contraseña es requerida'}, status=400)
            
            # Validar que el username no exista
            if User.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'error': 'El nombre de usuario ya existe'}, status=400)
            
            # Validar que el email no exista
            if User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'error': 'El email ya está registrado'}, status=400)
            
            # Crear el usuario
            try:
                propietario = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
            except Exception as e:
                return JsonResponse({'success': False, 'error': f'Error al crear usuario: {str(e)}'}, status=400)
            
            # Crear el restaurante con el propietario
            restaurante = Restaurante.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                propietario=propietario,
                activo=True
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Restaurante y usuario creados exitosamente',
                'restaurante': {
                    'id': restaurante.id,
                    'nombre': restaurante.nombre,
                    'slug': restaurante.slug
                },
                'usuario': {
                    'username': propietario.username,
                    'email': propietario.email
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


urlpatterns = [
    path('', redirect_to_login),
    
    # Redirección desde el login por defecto de Django a nuestro login personalizado
    path('accounts/login/', lambda request: redirect('/admin/web/login/'), name='fallback_login'),
    
    # Vista de login simple que funciona
    path('admin/web/login/', simple_login_view, name='simple_login'),
    
    # Dashboard web para admin
    path('admin/web/dashboard/', admin_dashboard_view, name='admin_dashboard'),
    
    # Dashboard web para restaurante individual
    path('admin/web/restaurant/', restaurant_dashboard_view, name='restaurant_dashboard'),
    
    # Editor completo para restaurante específico
    path('admin/web/restaurant/<slug:slug>/editor/', restaurant_editor_view, name='restaurant_editor'),
    
    # Vistas de gestión con templates existentes
    path('admin/manage/categories/', manage_categories_view, name='manage_categories'),
    path('admin/manage/foods/', manage_foods_view, name='manage_foods'),
    
    # API endpoints para edición inline
    path('admin/categoria/update/<int:categoria_id>/', update_categoria, name='update_categoria'),
    path('admin/categoria/delete/<int:categoria_id>/', delete_categoria, name='delete_categoria'),
    path('admin/comida/update/<int:comida_id>/', update_comida, name='update_comida'),
    path('admin/comida/delete/<int:comida_id>/', delete_comida, name='delete_comida'),
    
    # API endpoints para crear restaurantes
    path('admin/restaurante/create/', create_restaurante, name='create_restaurante'),
    path('admin/propietarios/', get_propietarios, name='get_propietarios'),
    
    # API endpoints para gestión
    path('api/categories/', api_categories, name='api_categories'),
    
    # URLs existentes que sabemos que funcionan
    path('admin/', admin.site.urls),
    path('api/', include('carta_restaurantes.api_urls')),
    path('api/admin/', include('carta_restaurantes.admin_urls')),
    path('debug/', debug_view),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
