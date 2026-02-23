"""
Admin Helpers - Funciones auxiliares para las vistas administrativas
"""
from .models import Restaurante


def get_user_restaurant(user):
    """
    Obtiene el restaurante asociado al usuario logueado.
    
    Args:
        user: Usuario autenticado
        
    Returns:
        - None si es superuser (tiene acceso a todos los restaurantes)
        - Restaurante instance si es propietario de un restaurante
        - None si no tiene restaurante asignado
    """
    if user.is_superuser:
        return None
    
    try:
        return Restaurante.objects.get(propietario=user, activo=True)
    except Restaurante.DoesNotExist:
        return None
