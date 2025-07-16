import React, { useState, useEffect } from "react";

function App() {
  const [categorias, setCategorias] = useState([]);
  const [comidas, setComidas] = useState([]);
  const [categoriaSeleccionada, setCategoriaSeleccionada] = useState(null);

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
    <div style={{ padding: 20 }}>
      {!categoriaSeleccionada ? (
        <>
          <h2>Seleccioná una categoría</h2>
          {categorias.map(cat => (
            <button key={cat.id} onClick={() => setCategoriaSeleccionada(cat.id)} style={{ margin: 5 }}>
              {cat.nombre}
            </button>
          ))}
        </>
      ) : (
        <>
          <button onClick={() => setCategoriaSeleccionada(null)}>⬅ Volver</button>
          <ul>
            {comidas.map(comida => (
              <li key={comida.id}>
                <strong>{comida.nombre}</strong> - ${comida.precio}<br />
                <em>{comida.descripcion}</em>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}

export default App;
