import React, { useState, useEffect } from 'react';
import styles from './Admin.module.css';

const API_BASE = 'http://localhost:8000/api/admin';

function Admin() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('adminToken'));
  
  // Estados de navegación jerárquica
  const [currentView, setCurrentView] = useState('categorias'); // 'categorias', 'subcategorias', 'comidas'
  const [selectedCategoria, setSelectedCategoria] = useState(null);
  const [selectedSubcategoria, setSelectedSubcategoria] = useState(null);
  
  // Estados de datos
  const [categorias, setCategorias] = useState([]);
  const [subcategorias, setSubcategorias] = useState([]);
  const [comidas, setComidas] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Estados para formularios
  const [showCategoriaForm, setShowCategoriaForm] = useState(false);
  const [showSubcategoriaForm, setShowSubcategoriaForm] = useState(false);
  const [showComidaForm, setShowComidaForm] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  // Formulario de login
  const [loginData, setLoginData] = useState({ username: '', password: '' });
  const [loginError, setLoginError] = useState('');

  useEffect(() => {
    if (token) {
      verifyToken();
    }
  }, [token]);

  useEffect(() => {
    if (user) {
      loadCurrentData();
    }
  }, [user, currentView, selectedCategoria, selectedSubcategoria]);

  const verifyToken = async () => {
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
    setCurrentView('categorias');
    setSelectedCategoria(null);
    setSelectedSubcategoria(null);
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

  // Funciones de carga de datos específicas
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

  const getTitle = () => {
    switch (currentView) {
      case 'categorias':
        return 'Categorías';
      case 'subcategorias':
        return `Subcategorías de ${selectedCategoria?.nombre}`;
      case 'comidas':
        return `Comidas de ${selectedSubcategoria?.nombre}`;
      default:
        return 'Panel de Administración';
    }
  };

  const getBreadcrumb = () => {
    const breadcrumbs = [];
    
    if (currentView === 'subcategorias' || currentView === 'comidas') {
      breadcrumbs.push(
        <button 
          key="categorias" 
          onClick={goToCategorias}
          className={styles.breadcrumbLink}
        >
          Categorías
        </button>
      );
    }
    
    if (currentView === 'comidas') {
      breadcrumbs.push(
        <span key="arrow1" className={styles.breadcrumbArrow}> → </span>,
        <button 
          key="subcategorias" 
          onClick={() => goToSubcategorias(selectedCategoria)}
          className={styles.breadcrumbLink}
        >
          {selectedCategoria?.nombre}
        </button>
      );
    }
    
    return breadcrumbs;
  };

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

  return (
    <div className={styles.adminContainer}>
      {/* Header */}
      <header className={styles.header}>
        <h1>Panel de Administración Victory</h1>
        <div className={styles.userInfo}>
          <span>Bienvenido, {user?.username}</span>
          <button onClick={handleLogout} className={styles.logoutButton}>Cerrar Sesión</button>
        </div>
      </header>

      {/* Main Content */}
      <main className={styles.mainContent}>
        <div className={styles.sectionHeader}>
          <div>
            <div className={styles.breadcrumb}>
              {getBreadcrumb()}
            </div>
            <h2>{getTitle()}</h2>
          </div>
          <button 
            className={styles.addButton}
            onClick={() => openNewForm(currentView)}
          >
            + Agregar {currentView === 'categorias' ? 'Categoría' : 
                     currentView === 'subcategorias' ? 'Subcategoría' : 'Comida'}
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
              />
            )}
            
            {currentView === 'subcategorias' && (
              <SubcategoriasGrid 
                subcategorias={subcategorias}
                onEdit={(item) => openEditForm(item, 'subcategorias')}
                onDelete={(id) => deleteItem(id, 'subcategorias')}
                onViewComidas={goToComidas}
              />
            )}
            
            {currentView === 'comidas' && (
              <ComidasGrid 
                comidas={comidas}
                onEdit={(item) => openEditForm(item, 'comidas')}
                onDelete={(id) => deleteItem(id, 'comidas')}
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
          onClose={() => {
            setShowCategoriaForm(false);
            setEditingItem(null);
          }}
          onSave={() => {
            loadCurrentData();
            setShowCategoriaForm(false);
            setEditingItem(null);
          }}
        />
      )}

      {showSubcategoriaForm && (
        <SubcategoriaForm
          item={editingItem}
          categoria={selectedCategoria}
          token={token}
          onClose={() => {
            setShowSubcategoriaForm(false);
            setEditingItem(null);
          }}
          onSave={() => {
            loadCurrentData();
            setShowSubcategoriaForm(false);
            setEditingItem(null);
          }}
        />
      )}

      {showComidaForm && (
        <ComidaForm
          item={editingItem}
          categoria={selectedCategoria}
          subcategoria={selectedSubcategoria}
          token={token}
          onClose={() => {
            setShowComidaForm(false);
            setEditingItem(null);
          }}
          onSave={() => {
            loadCurrentData();
            setShowComidaForm(false);
            setEditingItem(null);
          }}
        />
      )}
    </div>
  );
}

// Componente para grid de categorías
const CategoriasGrid = ({ categorias, onEdit, onDelete, onViewSubcategorias }) => (
  <div className={styles.cardGrid}>
    {categorias.map(categoria => (
      <div key={categoria.id} className={styles.categoryCard}>
        <div 
          className={styles.categoryImage}
          style={{
            backgroundImage: categoria.imagen ? `url(${categoria.imagen})` : 'none',
            backgroundColor: categoria.imagen ? 'transparent' : '#333'
          }}
        >
          {!categoria.imagen && (
            <div className={styles.noImageText}>Sin imagen</div>
          )}
        </div>
        <div className={styles.cardContent}>
          <h3 className={styles.cardTitle}>{categoria.nombre}</h3>
          <p className={styles.cardSubtitle}>Orden: {categoria.orden}</p>
          <div className={styles.cardActions}>
            <button 
              onClick={() => onViewSubcategorias(categoria)}
              className={styles.viewButton}
            >
              Ver Subcategorías
            </button>
            <button 
              onClick={() => onEdit(categoria)}
              className={styles.editButton}
            >
              Editar
            </button>
            <button 
              onClick={() => onDelete(categoria.id)}
              className={styles.deleteButton}
            >
              Eliminar
            </button>
          </div>
        </div>
      </div>
    ))}
  </div>
);

// Componente para grid de subcategorías
const SubcategoriasGrid = ({ subcategorias, onEdit, onDelete, onViewComidas }) => (
  <div className={styles.cardGrid}>
    {subcategorias.map(subcategoria => (
      <div key={subcategoria.id} className={styles.subcategoryCard}>
        <div className={styles.cardContent}>
          <h3 className={styles.cardTitle}>{subcategoria.nombre}</h3>
          <p className={styles.cardSubtitle}>Orden: {subcategoria.orden}</p>
          <div className={styles.cardActions}>
            <button 
              onClick={() => onViewComidas(subcategoria)}
              className={styles.viewButton}
            >
              Ver Comidas
            </button>
            <button 
              onClick={() => onEdit(subcategoria)}
              className={styles.editButton}
            >
              Editar
            </button>
            <button 
              onClick={() => onDelete(subcategoria.id)}
              className={styles.deleteButton}
            >
              Eliminar
            </button>
          </div>
        </div>
      </div>
    ))}
  </div>
);

// Componente para grid de comidas
const ComidasGrid = ({ comidas, onEdit, onDelete }) => (
  <div className={styles.cardGrid}>
    {comidas.map(comida => (
      <div key={comida.id} className={styles.foodCard}>
        <div className={styles.cardContent}>
          <h3 className={styles.cardTitle}>{comida.nombre}</h3>
          <p className={styles.cardPrice}>${comida.precio}</p>
          <p className={styles.cardDescription}>{comida.descripcion}</p>
          <p className={styles.cardAvailability}>
            {comida.disponible ? '✅ Disponible' : '❌ No disponible'}
          </p>
          <div className={styles.cardActions}>
            <button 
              onClick={() => onEdit(comida)}
              className={styles.editButton}
            >
              Editar
            </button>
            <button 
              onClick={() => onDelete(comida.id)}
              className={styles.deleteButton}
            >
              Eliminar
            </button>
          </div>
        </div>
      </div>
    ))}
  </div>
);

// Formulario para Categorías (simplificado)
const CategoriaForm = ({ item, token, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    nombre: item?.nombre || '',
    orden: item?.orden || 0
  });
  const [imageFile, setImageFile] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const data = new FormData();
    data.append('nombre', formData.nombre);
    data.append('orden', formData.orden);
    if (imageFile) {
      data.append('imagen', imageFile);
    }

    try {
      const url = item 
        ? `${API_BASE}/categorias/${item.id}/`
        : `${API_BASE}/categorias/`;
      
      const response = await fetch(url, {
        method: item ? 'PUT' : 'POST',
        headers: { 'Authorization': `Token ${token}` },
        body: data
      });

      if (response.ok) {
        onSave();
      }
    } catch (error) {
      console.error('Error guardando categoría:', error);
    }
  };

  return (
    <div className={styles.modalOverlay}>
      <div className={styles.modal}>
        <h3>{item ? 'Editar' : 'Nueva'} Categoría</h3>
        <form onSubmit={handleSubmit}>
          <div className={styles.formGroup}>
            <label>Nombre:</label>
            <input
              type="text"
              value={formData.nombre}
              onChange={(e) => setFormData({...formData, nombre: e.target.value})}
              required
            />
          </div>
          <div className={styles.formGroup}>
            <label>Orden:</label>
            <input
              type="number"
              value={formData.orden}
              onChange={(e) => setFormData({...formData, orden: parseInt(e.target.value)})}
              required
            />
          </div>
          <div className={styles.formGroup}>
            <label>Imagen:</label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setImageFile(e.target.files[0])}
            />
          </div>
          <div className={styles.formActions}>
            <button type="button" onClick={onClose}>Cancelar</button>
            <button type="submit">Guardar</button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Formulario para Subcategorías
const SubcategoriaForm = ({ item, categoria, token, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    nombre: item?.nombre || '',
    orden: item?.orden || 0,
    categoria: item?.categoria || categoria?.id || ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const url = item 
        ? `${API_BASE}/subcategorias/${item.id}/`
        : `${API_BASE}/subcategorias/`;
      
      const response = await fetch(url, {
        method: item ? 'PUT' : 'POST',
        headers: { 
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        onSave();
      }
    } catch (error) {
      console.error('Error guardando subcategoría:', error);
    }
  };

  return (
    <div className={styles.modalOverlay}>
      <div className={styles.modal}>
        <h3>{item ? 'Editar' : 'Nueva'} Subcategoría</h3>
        <form onSubmit={handleSubmit}>
          <div className={styles.formGroup}>
            <label>Nombre:</label>
            <input
              type="text"
              value={formData.nombre}
              onChange={(e) => setFormData({...formData, nombre: e.target.value})}
              required
            />
          </div>
          <div className={styles.formGroup}>
            <label>Orden:</label>
            <input
              type="number"
              value={formData.orden}
              onChange={(e) => setFormData({...formData, orden: parseInt(e.target.value)})}
              required
            />
          </div>
          <div className={styles.formActions}>
            <button type="button" onClick={onClose}>Cancelar</button>
            <button type="submit">Guardar</button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Formulario para Comidas
const ComidaForm = ({ item, categoria, subcategoria, token, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    nombre: item?.nombre || '',
    descripcion: item?.descripcion || '',
    precio: item?.precio || '',
    disponible: item?.disponible ?? true,
    categoria: item?.categoria || categoria?.id || '',
    subcategoria: item?.subcategoria || subcategoria?.id || ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const url = item 
        ? `${API_BASE}/comidas/${item.id}/`
        : `${API_BASE}/comidas/`;
      
      const response = await fetch(url, {
        method: item ? 'PUT' : 'POST',
        headers: { 
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        onSave();
      }
    } catch (error) {
      console.error('Error guardando comida:', error);
    }
  };

  return (
    <div className={styles.modalOverlay}>
      <div className={styles.modal}>
        <h3>{item ? 'Editar' : 'Nueva'} Comida</h3>
        <form onSubmit={handleSubmit}>
          <div className={styles.formGroup}>
            <label>Nombre:</label>
            <input
              type="text"
              value={formData.nombre}
              onChange={(e) => setFormData({...formData, nombre: e.target.value})}
              required
            />
          </div>
          <div className={styles.formGroup}>
            <label>Descripción:</label>
            <textarea
              value={formData.descripcion}
              onChange={(e) => setFormData({...formData, descripcion: e.target.value})}
            />
          </div>
          <div className={styles.formGroup}>
            <label>Precio:</label>
            <input
              type="number"
              step="0.01"
              value={formData.precio}
              onChange={(e) => setFormData({...formData, precio: e.target.value})}
              required
            />
          </div>
          <div className={styles.formGroup}>
            <label>
              <input
                type="checkbox"
                checked={formData.disponible}
                onChange={(e) => setFormData({...formData, disponible: e.target.checked})}
              />
              Disponible
            </label>
          </div>
          <div className={styles.formActions}>
            <button type="button" onClick={onClose}>Cancelar</button>
            <button type="submit">Guardar</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Admin;
