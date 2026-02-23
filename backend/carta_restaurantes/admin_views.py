"""
Admin Views - Sistema de Cartas Para Negocios
==============================================

ARCHIVO DE COMPATIBILIDAD - Re-exporta vistas desde módulos organizados:

Estructura modular:
- admin_helpers.py      → Funciones auxiliares (get_user_restaurant)
- admin_auth.py         → Autenticación (admin_login, verify_token)
- admin_dashboards.py   → Dashboards (admin_dashboard, simple_dashboard, test_dashboard)
- admin_crud.py         → CRUD (AdminCategoria*, AdminSubcategoria*, AdminComida*, update_*_orden)
- admin_debug.py        → Debug endpoints (setup_test_users, debug_*)

Este archivo mantiene la compatibilidad con imports existentes.
"""

# Helpers
from .admin_helpers import get_user_restaurant

# Autenticación
from .admin_auth import (
    admin_login,
    verify_token
)

# Dashboards
from .admin_dashboards import (
    admin_dashboard,
    simple_dashboard,
    test_dashboard
)

# CRUD
from .admin_crud import (
    AdminCategoriaList,
    AdminCategoriaDetail,
    AdminSubcategoriaList,
    AdminSubcategoriaDetail,
    AdminComidaList,
    AdminComidaDetail,
    update_categoria_orden,
    update_subcategoria_orden,
    update_comida_orden
)

# Debug (solo desarrollo)
from .admin_debug import (
    setup_test_users,
    debug_current_user,
    debug_real_data,
    debug_tokens
)

# __all__ para exposición explícita
__all__ = [
    # Helpers
    'get_user_restaurant',
    # Auth
    'admin_login',
    'verify_token',
    # Dashboards
    'admin_dashboard',
    'simple_dashboard',
    'test_dashboard',
    # CRUD - Categorías
    'AdminCategoriaList',
    'AdminCategoriaDetail',
    # CRUD - Subcategorías
    'AdminSubcategoriaList',
    'AdminSubcategoriaDetail',
    # CRUD - Comidas
    'AdminComidaList',
    'AdminComidaDetail',
    # Reordenamiento
    'update_categoria_orden',
    'update_subcategoria_orden',
    'update_comida_orden',
    # Debug
    'setup_test_users',
    'debug_current_user',
    'debug_real_data',
    'debug_tokens',
]
