// Formularios modales para el admin
import React, { useState, useEffect } from 'react';
import styles from './Admin.module.css';

const API_BASE = 'http://localhost:8000/api/admin';

// Formulario para Categorías
export const CategoriaForm = ({ item, token, onClose, onSave }) => {
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
export const SubcategoriaForm = ({ item, categoria, token, onClose, onSave }) => {
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
export const ComidaForm = ({ item, categoria, subcategoria, token, onClose, onSave }) => {
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