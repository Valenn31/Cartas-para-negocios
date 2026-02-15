// Componentes de grids para el admin
import React from 'react';
import styles from './Admin.module.css';

// Componente para grid de categorías con drag & drop
export const CategoriasGrid = ({ 
  categorias, 
  onEdit, 
  onDelete, 
  onViewSubcategorias,
  dragProps
}) => (
  <div className={styles.cardGrid}>
    {categorias.map(categoria => {
      const isDragging = dragProps?.draggedItem?.id === categoria.id;
      const isDragOver = dragProps?.dragOverItem?.id === categoria.id;
      
      return (
        <div 
          key={categoria.id} 
          className={`${styles.categoryCard} ${
            isDragging ? styles.dragging : ''
          } ${
            isDragOver ? styles.dragOver : ''
          }`}
          draggable={true}
          onDragStart={(e) => dragProps?.onDragStart(e, categoria)}
          onDragOver={(e) => dragProps?.onDragOver(e, categoria)}
          onDragLeave={dragProps?.onDragLeave}
          onDrop={(e) => dragProps?.onDrop(e, categoria)}
          onDragEnd={dragProps?.onDragEnd}
        >
          <div className={styles.dragHandle}>
            <span>⋮⋮</span>
          </div>
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
                onClick={(e) => {
                  e.stopPropagation();
                  onViewSubcategorias(categoria);
                }}
                className={styles.viewButton}
              >
                Ver Subcategorías
              </button>
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  onEdit(categoria);
                }}
                className={styles.editButton}
              >
                Editar
              </button>
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(categoria.id);
                }}
                className={styles.deleteButton}
              >
                Eliminar
              </button>
            </div>
          </div>
        </div>
      );
    })}
  </div>
);

// Componente para grid de subcategorías con drag & drop
export const SubcategoriasGrid = ({ 
  subcategorias, 
  onEdit, 
  onDelete, 
  onViewComidas,
  dragProps
}) => (
  <div className={styles.cardGrid}>
    {subcategorias.map(subcategoria => {
      const isDragging = dragProps?.draggedItem?.id === subcategoria.id;
      const isDragOver = dragProps?.dragOverItem?.id === subcategoria.id;
      
      return (
        <div 
          key={subcategoria.id} 
          className={`${styles.subcategoryCard} ${
            isDragging ? styles.dragging : ''
          } ${
            isDragOver ? styles.dragOver : ''
          }`}
          draggable={true}
          onDragStart={(e) => dragProps?.onDragStart(e, subcategoria)}
          onDragOver={(e) => dragProps?.onDragOver(e, subcategoria)}
          onDragLeave={dragProps?.onDragLeave}
          onDrop={(e) => dragProps?.onDrop(e, subcategoria)}
          onDragEnd={dragProps?.onDragEnd}
        >
          <div className={styles.dragHandle}>
            <span>⋮⋮</span>
          </div>
          <div className={styles.cardContent}>
            <h3 className={styles.cardTitle}>{subcategoria.nombre}</h3>
            <p className={styles.cardSubtitle}>Orden: {subcategoria.orden}</p>
            <div className={styles.cardActions}>
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  onViewComidas(subcategoria);
                }}
                className={styles.viewButton}
              >
                Ver Comidas
              </button>
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  onEdit(subcategoria);
                }}
                className={styles.editButton}
              >
                Editar
              </button>
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(subcategoria.id);
                }}
                className={styles.deleteButton}
              >
                Eliminar
              </button>
            </div>
          </div>
        </div>
      );
    })}
  </div>
);

// Componente para grid de comidas con drag & drop
export const ComidasGrid = ({ 
  comidas, 
  onEdit, 
  onDelete,
  dragProps
}) => (
  <div className={styles.cardGrid}>
    {comidas.map(comida => {
      const isDragging = dragProps?.draggedItem?.id === comida.id;
      const isDragOver = dragProps?.dragOverItem?.id === comida.id;
      
      return (
        <div 
          key={comida.id} 
          className={`${styles.foodCard} ${
            isDragging ? styles.dragging : ''
          } ${
            isDragOver ? styles.dragOver : ''
          }`}
          draggable={true}
          onDragStart={(e) => dragProps?.onDragStart(e, comida)}
          onDragOver={(e) => dragProps?.onDragOver(e, comida)}
          onDragLeave={dragProps?.onDragLeave}
          onDrop={(e) => dragProps?.onDrop(e, comida)}
          onDragEnd={dragProps?.onDragEnd}
        >
          <div className={styles.dragHandle}>
            <span>⋮⋮</span>
          </div>
          <div className={styles.cardContent}>
            <h3 className={styles.cardTitle}>{comida.nombre}</h3>
            <p className={styles.cardPrice}>${comida.precio}</p>
            <p className={styles.cardDescription}>{comida.descripcion}</p>
            <p className={styles.cardSubtitle}>Orden: {comida.orden || 'No definido'}</p>
            <p className={styles.cardAvailability}>
              {comida.disponible ? '✅ Disponible' : '❌ No disponible'}
            </p>
            <div className={styles.cardActions}>
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  onEdit(comida);
                }}
                className={styles.editButton}
              >
                Editar
              </button>
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(comida.id);
                }}
                className={styles.deleteButton}
              >
                Eliminar
              </button>
            </div>
          </div>
        </div>
      );
    })}
  </div>
);