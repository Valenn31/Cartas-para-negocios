import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import styles from './Admin.module.css';
import { useAuth, useAdminData, useDragDrop } from './AdminHooks';
import { CategoriasGrid, SubcategoriasGrid, ComidasGrid } from './AdminComponents';
import { CategoriaForm, SubcategoriaForm, ComidaForm } from './AdminForms';
import { getTitle, getBreadcrumb, getAddButtonText } from './AdminUtils';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://cartas-para-negocios-production.up.railway.app';
const API_BASE = `${API_BASE_URL}/api/admin`;

function Admin() {
  // Obtener el slug del restaurante de los parámetros de la URL
  const { restaurant_slug } = useParams();
  
  // Estados de navegación
  const [currentView, setCurrentView] = useState('categorias');
  const [selectedCategoria, setSelectedCategoria] = useState(null);
  const [selectedSubcategoria, setSelectedSubcategoria] = useState(null);
  
  // Estados de formularios
  const [showCategoriaForm, setShowCategoriaForm] = useState(false);
  const [showSubcategoriaForm, setShowSubcategoriaForm] = useState(false);
  const [showComidaForm, setShowComidaForm] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  // Hooks personalizados
  const { 
    user, 
    token, 
    loginData, 
    setLoginData, 
    loginError, 
    verifyToken, 
    handleLogin, 
    handleLogout 
  } = useAuth();

  const {
    categorias,
    setCategorias,
    subcategorias, 
    setSubcategorias,
    comidas,
    setComidas,
    loading,
    loadCurrentData,
    deleteItem
  } = useAdminData(token, currentView, selectedCategoria, selectedSubcategoria, restaurant_slug);

  // Hooks de drag & drop para cada tipo
  const categoriasDrag = useDragDrop(
    token, 
    categorias, 
    setCategorias, 
    `${API_BASE}/categorias/orden/`,
    restaurant_slug
  );

  const subcategoriasDrag = useDragDrop(
    token, 
    subcategorias, 
    setSubcategorias, 
    `${API_BASE}/subcategorias/orden/`,
    restaurant_slug
  );
  const comidasDrag = useDragDrop(
    token, 
    comidas, 
    setComidas, 
    `${API_BASE}/comidas/orden/`,
    restaurant_slug
  );
  // Effects
  useEffect(() => {
    if (token) verifyToken();
  }, [token]);

  // Protección: redirigir si no hay autenticación válida
  useEffect(() => {
    // Si no hay token, redirigir al login de Railway
    if (!token) {
      window.location.href = 'https://cartas-para-negocios-production.up.railway.app/admin/web/login/';
      return;
    }
  }, [token]);

  // Protección adicional: si el token es inválido, redirigir también
  useEffect(() => {
    if (token && !user && !loading) {
      // Token existe pero el usuario no se pudo verificar
      setTimeout(() => {
        if (!user) {
          localStorage.removeItem('admin_token');
          window.location.href = 'https://cartas-para-negocios-production.up.railway.app/admin/web/login/';
        }
      }, 3000); // Dar 3 segundos para que se verifique
    }
  }, [token, user, loading]);

  useEffect(() => {
    if (user) loadCurrentData();
  }, [user, currentView, selectedCategoria, selectedSubcategoria]);

  // Funciones de navegación
  const goToCategorias = () => {
    setCurrentView('categorias');
    setSelectedCategoria(null);
    setSelectedSubcategoria(null);
  };

  const goToSubcategorias = (categoria) => {
    setSelectedCategoria(categoria);
    setCurrentView('subcategorias');
    setSelectedSubcategoria(null);
  };

  const goToComidas = (subcategoria) => {
    setSelectedSubcategoria(subcategoria);
    setCurrentView('comidas');
  };

  // Funciones de formularios
  const openEditForm = (item, type) => {
    setEditingItem({ ...item, type });
    
    switch (type) {
      case 'categorias':
        setShowCategoriaForm(true);
        break;
      case 'subcategorias':
        setShowSubcategoriaForm(true);
        break;
      case 'comidas':
        setShowComidaForm(true);
        break;
    }
  };

  const openNewForm = (type) => {
    setEditingItem(null);
    
    switch (type) {
      case 'categorias':
        setShowCategoriaForm(true);
        break;
      case 'subcategorias':
        setShowSubcategoriaForm(true);
        break;
      case 'comidas':
        setShowComidaForm(true);
        break;
    }
  };

  const closeForm = () => {
    setShowCategoriaForm(false);
    setShowSubcategoriaForm(false);
    setShowComidaForm(false);
    setEditingItem(null);
  };

  const handleFormSave = () => {
    loadCurrentData();
    closeForm();
  };

  // Si no hay token, mostrar pantalla de redirección
  if (!token) {
    return (
      <div className={styles.loginContainer}>
        <div className={styles.loginBox}>
          <h1 className={styles.loginTitle}>Editor Completo - Acceso Protegido</h1>
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <div style={{ marginBottom: '20px' }}>
              <i className="fas fa-lock" style={{ fontSize: '48px', color: '#667eea', marginBottom: '20px' }}></i>
            </div>
            <h2>Acceso Restringido</h2>
            <p>Este editor es exclusivo para usuarios autenticados.</p>
            <p>Redirigiendo al sistema de login...</p>
            <div style={{ marginTop: '20px' }}>
              <div className="spinner" style={{
                border: '4px solid #f3f3f3',
                borderTop: '4px solid #667eea', 
                borderRadius: '50%',
                width: '40px',
                height: '40px',
                animation: 'spin 1s linear infinite',
                margin: '0 auto'
              }}></div>
            </div>
            <a 
              href="https://cartas-para-negocios-production.up.railway.app/admin/web/login/"
              style={{
                display: 'inline-block',
                marginTop: '20px',
                padding: '10px 20px',
                backgroundColor: '#667eea',
                color: 'white',
                textDecoration: 'none',
                borderRadius: '5px'
              }}
            >
              Ir al Login Manual
            </a>
          </div>
        </div>
      </div>
    );
  }

  // Componente principal del Admin
  return (
    <div className={styles.adminContainer}>
      {/* Header */}
      <header className={styles.header}>
        <h1>Panel de Administración Victory</h1>
        <div className={styles.userInfo}>
          <span>Bienvenido, {user?.username}</span>
          <button onClick={handleLogout} className={styles.logoutButton}>
            Cerrar Sesión
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className={styles.mainContent}>
        <div className={styles.sectionHeader}>
          <div>
            <div className={styles.breadcrumb}>
              {getBreadcrumb(currentView, selectedCategoria, goToCategorias, goToSubcategorias)}
            </div>
            <h2>{getTitle(currentView, selectedCategoria, selectedSubcategoria)}</h2>
          </div>
          <button 
            className={styles.addButton}
            onClick={() => openNewForm(currentView)}
          >
            {getAddButtonText(currentView)}
          </button>
        </div>

        {loading ? (
          <div className={styles.loading}>Cargando...</div>
        ) : (
          <div className={styles.dataContainer}>
            {currentView === 'categorias' && (
              <CategoriasGrid 
                categorias={categorias}
                onEdit={(item) => openEditForm(item, 'categorias')}
                onDelete={(id) => deleteItem(id, 'categorias')}
                onViewSubcategorias={goToSubcategorias}
                dragProps={categoriasDrag}
              />
            )}
            
            {currentView === 'subcategorias' && (
              <SubcategoriasGrid 
                subcategorias={subcategorias}
                onEdit={(item) => openEditForm(item, 'subcategorias')}
                onDelete={(id) => deleteItem(id, 'subcategorias')}
                onViewComidas={goToComidas}
                dragProps={subcategoriasDrag}
              />
            )}
            
            {currentView === 'comidas' && (
              <ComidasGrid 
                comidas={comidas}
                onEdit={(item) => openEditForm(item, 'comidas')}
                onDelete={(id) => deleteItem(id, 'comidas')}
                dragProps={comidasDrag}
              />
            )}
          </div>
        )}
      </main>

      {/* Formularios modales */}
      {showCategoriaForm && (
        <CategoriaForm
          item={editingItem}
          token={token}
          restaurant_slug={restaurant_slug}
          onClose={closeForm}
          onSave={handleFormSave}
        />
      )}

      {showSubcategoriaForm && (
        <SubcategoriaForm
          item={editingItem}
          categoria={selectedCategoria}
          token={token}
          restaurant_slug={restaurant_slug}
          onClose={closeForm}
          onSave={handleFormSave}
        />
      )}

      {showComidaForm && (
        <ComidaForm
          item={editingItem}
          categoria={selectedCategoria}
          subcategoria={selectedSubcategoria}
          token={token}
          restaurant_slug={restaurant_slug}
          onClose={closeForm}
          onSave={handleFormSave}
        />
      )}
    </div>
  );
}

export default Admin;