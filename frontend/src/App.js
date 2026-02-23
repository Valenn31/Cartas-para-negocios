import React, { useState, useEffect } from "react";
import styles from "./App.module.css";

function App() {
  const [categorias, setCategorias] = useState([]);
  const [subcategoriasConComidas, setSubcategoriasConComidas] = useState([]);
  const [categoriaSeleccionada, setCategoriaSeleccionada] = useState(null);
  const [restauranteSlug, setRestauranteSlug] = useState(null);
  const [restauranteNombre, setRestauranteNombre] = useState('Cargando...');

  const API_BASE = process.env.REACT_APP_API_URL || 'https://cartas-para-negocios-production.up.railway.app';

  // Obtener parámetro del restaurante desde la URL
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const restaurante = urlParams.get('restaurante');
    
    if (restaurante) {
      setRestauranteSlug(restaurante);
      // Capitalizar nombre del restaurante para mostrar
      setRestauranteNombre(restaurante.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()));
    } else {
      // Si no hay parámetro de restaurante, mostrar error
      setRestauranteNombre('Error: Restaurante no especificado');
    }
  }, []);

  // Eliminar márgenes y padding del body
  useEffect(() => {
    document.body.style.margin = "0";
    document.body.style.padding = "0";
    document.body.style.backgroundColor = "#0f0f0f";
    document.body.style.fontFamily = "'Montserrat', sans-serif";
  }, []);

  // Cargar categorías cuando tengamos el slug del restaurante
  useEffect(() => {
    if (restauranteSlug) {
      fetch(`${API_BASE}/api/categorias/?restaurante=${restauranteSlug}`)
        .then(res => res.json())
        .then(data => {
          setCategorias(data);
          console.log('Categorías cargadas para', restauranteSlug, ':', data);
        })
        .catch(error => {
          console.error('Error cargando categorías:', error);
          setCategorias([]);
        });
    }
  }, [restauranteSlug, API_BASE]);

  // Cargar subcategorías y sus comidas cuando se selecciona una categoría
  useEffect(() => {
    if (categoriaSeleccionada && restauranteSlug) {
      // Primero obtenemos las subcategorías
      fetch(`${API_BASE}/api/categorias/${categoriaSeleccionada}/subcategorias/?restaurante=${restauranteSlug}`)
        .then(res => res.json())
        .then(async (subcategorias) => {
          // Para cada subcategoría, obtenemos sus comidas
          const subcategoriasConComidas = await Promise.all(
            subcategorias.map(async (subcategoria) => {
              const comidasResponse = await fetch(`${API_BASE}/api/subcategorias/${subcategoria.id}/comidas/?restaurante=${restauranteSlug}`);
              const comidas = await comidasResponse.json();
              return {
                ...subcategoria,
                comidas: comidas
              };
            })
          );
          setSubcategoriasConComidas(subcategoriasConComidas);
        });
    }
  }, [categoriaSeleccionada]);

  const volverACategorias = () => {
    setCategoriaSeleccionada(null);
    setSubcategoriasConComidas([]);
  };

  return (
    <div className={styles.container}>
      {!categoriaSeleccionada ? (
        // Vista principal - Categorías
        <>
          {/* Header elegante */}
          <div className={styles.header}>
            <h1 className={styles.headerTitle}>
              {restauranteNombre}
            </h1>
            <p className={styles.headerSubtitle}>
              {restauranteSlug ? 'BIENVENIDOS A NUESTRO MENÚ' : 'ERROR: RESTAURANTE NO ENCONTRADO'}
            </p>
          </div>

          {/* Degradado de transición */}
          <div className={styles.headerGradient}></div>

          <div className={styles.categoriesSection}>
            <h2 className={styles.categoriesTitle}>
              
            </h2>

            <div className={styles.categoriesGrid}>
              {!restauranteSlug ? (
                <div style={{textAlign: 'center', color: '#ff6b6b', padding: '40px'}}>
                  <h3>Error: No se especificó un restaurante</h3>
                  <p>La URL debe contener ?restaurante=nombre-del-restaurante</p>
                </div>
              ) : categorias.length === 0 ? (
                <div style={{textAlign: 'center', color: '#ccc', padding: '40px'}}>
                  <h3>Cargando menú...</h3>
                  <p>O este restaurante aún no tiene categorías configuradas</p>
                </div>
              ) : (
                categorias.map(cat => (
                  <div
                    key={cat.id}
                    onClick={() => setCategoriaSeleccionada(cat.id)}
                    className={styles.categoryCard}
                    style={{
                      backgroundImage: `url(${cat.imagen})`
                    }}
                  >
                    <div className={styles.categoryOverlay}>
                      {cat.nombre}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
          
          {/* Footer */}
          <div className={styles.footer}>
            <p className={styles.footerText}>
              Victory © 2025
            </p>
            <a href="/admin" className={styles.adminLink}>
              Admin
            </a>
          </div>
        </>
      ) : (
        // Vista estilo Victory - Subcategorías con comidas agrupadas
        <div className={styles.menuView}>
          <div 
            className={styles.menuHeader}
            style={{
              backgroundImage: `url(${categorias.find(cat => cat.id === categoriaSeleccionada)?.imagen})`
            }}
          >
            <div className={styles.menuHeaderOverlay}></div>
            <button 
              onClick={volverACategorias}
              className={styles.backButton}
            >
              ⬅
            </button>
            <h2 className={styles.categoryTitle}>
              {categorias.find(cat => cat.id === categoriaSeleccionada)?.nombre || 'Categoría'}
            </h2>
          </div>

          {/* Lista de subcategorías con sus comidas */}
          <div className={styles.menuContent}>
            {subcategoriasConComidas.map((subcategoria, index) => (
              <div key={subcategoria.id} className={styles.subcategorySection}>
                {/* Título de la subcategoría */}
                <h3 className={styles.subcategoryTitle}>
                  {subcategoria.nombre}
                </h3>

                {/* Grid de comidas de esta subcategoría */}
                <div className={styles.foodGrid}>
                  {subcategoria.comidas.map((comida, comidaIndex) => (
                    <div
                      key={comida.id}
                      className={styles.foodCard}
                      style={{
                        animationDelay: `${(index * 0.3) + (comidaIndex * 0.1)}s`
                      }}
                    >
                      <h4 className={styles.foodName}>
                        {comida.nombre}
                      </h4>
                      
                      <div className={styles.foodPrice}>
                        ${comida.precio}
                      </div>
                      
                      <p className={styles.foodDescription}>
                        {comida.descripcion}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
          
          <div className={styles.footer}>
            <p className={styles.footerText}>
              Victory © 2025
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
