// Login functionality
document.addEventListener('DOMContentLoaded', function() {
    // Login form handling
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
});

async function handleLogin(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    const username = formData.get('username');
    const password = formData.get('password');
    
    if (!username || !password) {
        showError('Por favor completa todos los campos');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/admin/auth/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Save token
            localStorage.setItem('admin_token', data.token);
            
            // Show success and redirect
            showSuccess('¡Login exitoso! Redirigiendo...');
            setTimeout(() => {
                window.location.href = '/admin/web/';
            }, 1000);
        } else {
            showError(data.error || 'Error en el login');
        }
    } catch (error) {
        console.error('Login error:', error);
        showError('Error de conexión. Intenta de nuevo.');
    } finally {
        showLoading(false);
    }
}

function fillDemo(username, password) {
    document.getElementById('username').value = username;
    document.getElementById('password').value = password;
}

function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        if (show) {
            overlay.classList.add('show');
        } else {
            overlay.classList.remove('show');
        }
    }
}

function showError(message) {
    const alert = document.getElementById('errorAlert');
    const messageEl = document.getElementById('errorMessage');
    
    if (alert && messageEl) {
        messageEl.textContent = message;
        alert.classList.add('show');
        
        // Auto hide after 5 seconds
        setTimeout(() => {
            alert.classList.remove('show');
        }, 5000);
    }
}

function showSuccess(message) {
    // Create success alert if it doesn't exist
    let successAlert = document.getElementById('successAlert');
    if (!successAlert) {
        successAlert = document.createElement('div');
        successAlert.id = 'successAlert';
        successAlert.className = 'alert alert-success';
        successAlert.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span id="successMessage"></span>
            <button onclick="closeSuccessAlert()" class="close-btn">&times;</button>
        `;
        document.body.appendChild(successAlert);
        
        // Add success alert styles
        const style = document.createElement('style');
        style.textContent = `
            .alert-success {
                background: #f0f9ff;
                border: 1px solid #bae6fd;
                color: #0369a1;
            }
        `;
        document.head.appendChild(style);
    }
    
    const messageEl = document.getElementById('successMessage');
    messageEl.textContent = message;
    successAlert.classList.add('show');
}

function closeAlert() {
    const alert = document.getElementById('errorAlert');
    if (alert) {
        alert.classList.remove('show');
    }
}

function closeSuccessAlert() {
    const alert = document.getElementById('successAlert');
    if (alert) {
        alert.classList.remove('show');
    }
}

function getCSRFToken() {
    // Buscar en cookies primero
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    
    // Buscar en input hidden como fallback
    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (csrfInput) {
        return csrfInput.value;
    }
    
    // Buscar en meta tag como último recurso
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    if (csrfMeta) {
        return csrfMeta.getAttribute('content');
    }
    
    return '';
}

// Dashboard functionality
function toggleQuickActions() {
    const menu = document.querySelector('.quick-actions-menu');
    if (menu) {
        menu.classList.toggle('active');
    }
}

// Close quick actions when clicking outside
document.addEventListener('click', function(e) {
    const quickActions = document.querySelector('.quick-actions');
    if (quickActions && !e.target.closest('.quick-actions')) {
        const menu = document.querySelector('.quick-actions-menu');
        if (menu) {
            menu.classList.remove('active');
        }
    }
});

// Auto-update dashboard stats
function updateDashboardStats() {
    const token = localStorage.getItem('admin_token');
    if (!token) return;
    
    fetch('/api/admin/dashboard/stats/', {
        headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.stats) {
            updateStatCard('categorias', data.stats.total_categorias);
            updateStatCard('comidas', data.stats.total_comidas);
            updateStatCard('precio', data.stats.promedio_precio);
        }
    })
    .catch(error => console.error('Error updating stats:', error));
}

function updateStatCard(type, value) {
    const selector = `.stat-card:nth-child(${getStatCardIndex(type)}) .stat-content h3`;
    const element = document.querySelector(selector);
    if (element) {
        element.textContent = value || '0';
    }
}

function getStatCardIndex(type) {
    switch (type) {
        case 'categorias': return 1;
        case 'comidas': return 2;
        case 'restaurante': return 3;
        case 'precio': return 4;
        default: return 1;
    }
}

// Initialize dashboard if we're on the dashboard page
document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname.includes('/admin/web/')) {
        // Update stats every 30 seconds
        setInterval(updateDashboardStats, 30000);
    }
});

// Logout functionality
function logout() {
    localStorage.removeItem('admin_token');
    window.location.href = '/admin/web/login/';
}

// Add smooth animations
document.addEventListener('DOMContentLoaded', function() {
    // Animate cards on load
    const cards = document.querySelectorAll('.stat-card, .restaurant-info-card, .categories-preview-card, .activity-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR'
    }).format(amount || 0);
}

function formatDate(dateString) {
    return new Intl.DateTimeFormat('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(dateString));
}

// Export functions for use in other scripts
window.AdminUtils = {
    showError,
    showSuccess,
    showLoading,
    toggleQuickActions,
    logout,
    updateDashboardStats,
    formatCurrency,
    formatDate
};