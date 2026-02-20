from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.shortcuts import redirect, render

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
                        showAlert('¡Login exitoso! Token: ' + data.token.substring(0, 20) + '...', 'success');
                        setTimeout(() => {
                            window.location.href = '/api/admin/test/?token=' + data.token;
                        }, 2000);
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

urlpatterns = [
    path('', redirect_to_login),
    
    # Vista de login simple que funciona
    path('admin/web/login/', simple_login_view, name='simple_login'),
    
    # URLs existentes que sabemos que funcionan
    path('admin/', admin.site.urls),
    path('api/', include('carta_restaurantes.api_urls')),
    path('api/admin/', include('carta_restaurantes.admin_urls')),
    path('debug/', debug_view),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
