import React, { useState, useEffect } from 'react';
import styles from './Admin.module.css';
import { useAuth, useAdminData, useDragDrop } from './AdminHooks';
import { CategoriasGrid, SubcategoriasGrid, ComidasGrid } from './AdminComponents';
import { CategoriaForm, SubcategoriaForm, ComidaForm } from './AdminForms';
import { getTitle, getBreadcrumb, getAddButtonText } from './AdminUtils';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_BASE = `${API_BASE_URL}/api/admin`;

function Admin() {
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
  } = useAdminData(token, currentView, selectedCategoria, selectedSubcategoria);

  // Hooks de drag & drop para cada tipo
  const categoriasDrag = useDragDrop(
    token, 
    categorias, 
    setCategorias, 
    `${API_BASE}/categorias/orden/`
  );

  const subcategoriasDrag = useDragDrop(
    token, 
    subcategorias, 
    setSubcategorias, 
    `${API_BASE}/subcategorias/orden/`
  );
  const comidasDrag = useDragDrop(
    token, 
    comidas, 
    setComidas, 
    `${API_BASE}/comidas/orden/`
  );
  // Effects
  useEffect(() => {
    if (token) verifyToken();
  }, [token]);

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

  // Componente de Login
  if (!token) {
    return (
      <div className={styles.loginContainer}>
        <div className={styles.loginBox}>
          <h1 className={styles.loginTitle}>Administración Victory</h1>
          <form onSubmit={handleLogin} className={styles.loginForm}>
            <div className={styles.formGroup}>
              <label>Usuario:</label>
              <input
                type="text"
                value={loginData.username}
                onChange={(e) => setLoginData({...loginData, username: e.target.value})}
                required
              />
            </div>
            <div className={styles.formGroup}>
              <label>Contraseña:</label>
              <input
                type="password"
                value={loginData.password}
                onChange={(e) => setLoginData({...loginData, password: e.target.value})}
                required
              />
            </div>
            {loginError && <div className={styles.error}>{loginError}</div>}
            <button type="submit" className={styles.loginButton}>Ingresar</button>
          </form>
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
          onClose={closeForm}
          onSave={handleFormSave}
        />
      )}

      {showSubcategoriaForm && (
        <SubcategoriaForm
          item={editingItem}
          categoria={selectedCategoria}
          token={token}
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
          onClose={closeForm}
          onSave={handleFormSave}
        />
      )}
    </div>
  );
}

export default Admin;