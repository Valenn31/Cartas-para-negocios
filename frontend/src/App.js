import React, { useState, useEffect } from "react";
import styles from "./App.module.css";

function App() {
  const [categorias, setCategorias] = useState([]);
  const [comidas, setComidas] = useState([]);
  const [categoriaSeleccionada, setCategoriaSeleccionada] = useState(null);

  // Eliminar márgenes y padding del body
  useEffect(() => {
    document.body.style.margin = "0";
    document.body.style.padding = "0";
    document.body.style.backgroundColor = "#1a1a1a";
    document.body.style.fontFamily = "'Montserrat', sans-serif";
  }, []);

  useEffect(() => {
    fetch("http://localhost:8000/api/categorias/")
      .then(res => res.json())
      .then(data => setCategorias(data));
  }, []);

  useEffect(() => {
    if (categoriaSeleccionada) {
      fetch("http://localhost:8000/api/comidas/")
        .then(res => res.json())
        .then(data =>
          setComidas(data.filter(c => c.categoria === categoriaSeleccionada))
        );
    }
  }, [categoriaSeleccionada]);

  return (
    <div className={styles.container}>
      {!categoriaSeleccionada ? (
        <>
          {/* Header elegante */}
          <div className={styles.header}>
            <h1 className={styles.headerTitle}>
              Victory
            </h1>
            <p className={styles.headerSubtitle}>
              BIENVENIDOS
            </p>
          </div>

          <div className={styles.categoriesSection}>
            <h2 className={styles.categoriesTitle}>
              
            </h2>

            <div className={styles.categoriesGrid}>
              {categorias.map(cat => (
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
              ))}
            </div>
          </div>
        </>
      ) : (
        <div className={styles.menuView}>
          {/* Header con botón volver */}
          <div 
            className={styles.menuHeader}
            style={{
              backgroundImage: `url(${categorias.find(cat => cat.id === categoriaSeleccionada)?.imagen})`
            }}
          >
            <div className={styles.menuHeaderOverlay}></div>
            <button 
              onClick={() => setCategoriaSeleccionada(null)}
              className={styles.backButton}
            >
              ⬅
            </button>
            <h2 className={styles.categoryTitle}>
              {categorias.find(cat => cat.id === categoriaSeleccionada)?.nombre || 'Categoría'}
            </h2>
          </div>

          {/* Grid de comidas */}
          <div className={styles.foodSection}>
            <div className={styles.foodGrid}>
              {comidas.map(comida => (
                <div
                  key={comida.id}
                  className={styles.foodCard}
                >
                  <h3 className={styles.foodName}>
                    {comida.nombre}
                  </h3>
                  
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
        </div>
      )}
    </div>
  );
}

export default App;
