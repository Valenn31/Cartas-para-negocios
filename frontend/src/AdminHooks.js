// Hooks personalizados para el admin
import { useState, useEffect } from 'react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_BASE = `${API_BASE_URL}/api/admin`;

// Hook para autenticación
export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('adminToken'));
  const [loginData, setLoginData] = useState({ username: '', password: '' });
  const [loginError, setLoginError] = useState('');

  const verifyToken = async () => {
    if (!token) return;
    
    try {
      const response = await fetch(`${API_BASE}/auth/verify/`, {
        headers: { 'Authorization': `Token ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
      } else {
        localStorage.removeItem('adminToken');
        setToken(null);
      }
    } catch (error) {
      console.error('Error verificando token:', error);
      localStorage.removeItem('adminToken');
      setToken(null);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError('');
    
    try {
      const response = await fetch(`${API_BASE}/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginData)
      });
      
      const data = await response.json();
      
      if (response.ok) {
        localStorage.setItem('adminToken', data.token);
        setToken(data.token);
        setUser(data.user);
      } else {
        setLoginError(data.error || 'Error de autenticación');
      }
    } catch (error) {
      setLoginError('Error de conexión');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('adminToken');
    setToken(null);
    setUser(null);
  };

  return {
    user,
    token,
    loginData,
    setLoginData,
    loginError,
    verifyToken,
    handleLogin,
    handleLogout
  };
};

// Hook para datos
export const useAdminData = (token, currentView, selectedCategoria, selectedSubcategoria) => {
  const [categorias, setCategorias] = useState([]);
  const [subcategorias, setSubcategorias] = useState([]);
  const [comidas, setComidas] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadCategorias = async () => {
    try {
      const response = await fetch(`${API_BASE}/categorias/`, {
        headers: { 'Authorization': `Token ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setCategorias(data);
      }
    } catch (error) {
      console.error('Error cargando categorías:', error);
    }
  };

  const loadSubcategoriasByCategoria = async (categoriaId) => {
    try {
      const response = await fetch(`${API_BASE}/categorias/${categoriaId}/subcategorias/`, {
        headers: { 'Authorization': `Token ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setSubcategorias(data);
      }
    } catch (error) {
      console.error('Error cargando subcategorías:', error);
    }
  };

  const loadComidasBySubcategoria = async (subcategoriaId) => {
    try {
      const response = await fetch(`${API_BASE}/subcategorias/${subcategoriaId}/comidas/`, {
        headers: { 'Authorization': `Token ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setComidas(data);
      }
    } catch (error) {
      console.error('Error cargando comidas:', error);
    }
  };

  const loadCurrentData = async () => {
    setLoading(true);
    try {
      if (currentView === 'categorias') {
        await loadCategorias();
      } else if (currentView === 'subcategorias' && selectedCategoria) {
        await loadSubcategoriasByCategoria(selectedCategoria.id);
      } else if (currentView === 'comidas' && selectedSubcategoria) {
        await loadComidasBySubcategoria(selectedSubcategoria.id);
      }
    } catch (error) {
      console.error('Error cargando datos:', error);
    }
    setLoading(false);
  };

  const deleteItem = async (id, type) => {
    if (!window.confirm('¿Estás seguro de eliminar este elemento?')) return;
    
    try {
      const response = await fetch(`${API_BASE}/${type}/${id}/`, {
        method: 'DELETE',
        headers: { 'Authorization': `Token ${token}` }
      });
      
      if (response.ok) {
        loadCurrentData();
      }
    } catch (error) {
      console.error('Error eliminando:', error);
    }
  };

  return {
    categorias,
    setCategorias,
    subcategorias,
    setSubcategorias,
    comidas,
    setComidas,
    loading,
    loadCurrentData,
    deleteItem
  };
};

// Hook para drag & drop
export const useDragDrop = (token, items, setItems, updateOrderUrl) => {
  const [draggedItem, setDraggedItem] = useState(null);
  const [dragOverItem, setDragOverItem] = useState(null);

  const updateOrder = async (reorderedItems) => {
    try {
      const orders = reorderedItems.map((item, index) => ({
        id: item.id,
        orden: index + 1
      }));
      
      const response = await fetch(updateOrderUrl, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ orders })
      });
      
      if (response.ok) {
        setItems(reorderedItems.map((item, index) => ({
          ...item,
          orden: index + 1
        })));
      }
    } catch (error) {
      console.error('Error actualizando orden:', error);
    }
  };

  const handleDragStart = (e, item) => {
    setDraggedItem(item);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e, item) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOverItem(item);
  };

  const handleDragLeave = () => {
    setDragOverItem(null);
  };

  const handleDrop = (e, dropTarget) => {
    e.preventDefault();
    
    if (!draggedItem || draggedItem.id === dropTarget.id) {
      setDraggedItem(null);
      setDragOverItem(null);
      return;
    }

    const currentItems = [...items];
    const draggedIndex = currentItems.findIndex(item => item.id === draggedItem.id);
    const targetIndex = currentItems.findIndex(item => item.id === dropTarget.id);

    const [movedItem] = currentItems.splice(draggedIndex, 1);
    currentItems.splice(targetIndex, 0, movedItem);

    updateOrder(currentItems);
    
    setDraggedItem(null);
    setDragOverItem(null);
  };

  const handleDragEnd = () => {
    setDraggedItem(null);
    setDragOverItem(null);
  };

  return {
    draggedItem,
    dragOverItem,
    onDragStart: handleDragStart,
    onDragOver: handleDragOver,
    onDragLeave: handleDragLeave,
    onDrop: handleDrop,
    onDragEnd: handleDragEnd
  };
};