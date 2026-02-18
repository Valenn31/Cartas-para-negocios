// Funciones utilitarias para el admin
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_BASE = `${API_BASE_URL}/api/admin`;

// Generar título según la vista actual
export const getTitle = (currentView, selectedCategoria, selectedSubcategoria) => {
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

// Generar breadcrumb de navegación
export const getBreadcrumb = (currentView, selectedCategoria, goToCategorias, goToSubcategorias) => {
  const breadcrumbs = [];
  
  if (currentView === 'subcategorias' || currentView === 'comidas') {
    breadcrumbs.push(
      <button 
        key="categorias" 
        onClick={goToCategorias}
        className="breadcrumbLink"
      >
        Categorías
      </button>
    );
  }
  
  if (currentView === 'comidas') {
    breadcrumbs.push(
      <span key="arrow1" className="breadcrumbArrow"> → </span>,
      <button 
        key="subcategorias" 
        onClick={() => goToSubcategorias(selectedCategoria)}
        className="breadcrumbLink"
      >
        {selectedCategoria?.nombre}
      </button>
    );
  }
  
  return breadcrumbs;
};

// Obtener texto del botón agregar según la vista
export const getAddButtonText = (currentView) => {
  switch (currentView) {
    case 'categorias':
      return '+ Agregar Categoría';
    case 'subcategorias':
      return '+ Agregar Subcategoría';
    case 'comidas':
      return '+ Agregar Comida';
    default:
      return '+ Agregar';
  }
};