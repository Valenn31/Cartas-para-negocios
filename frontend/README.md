# Carta QR - Frontend

React application para mostrar cartas de restaurante con códigos QR.

## 🚀 Deploy en Vercel

### Preparación

1. **Construir el proyecto localmente** (opcional, para probar):
   ```bash
   npm run build
   ```

2. **Variables de entorno necesarias en Vercel**:
   - `REACT_APP_API_URL`: URL de tu API backend

### Deploy automático

1. **Conectar repositorio a Vercel:**
   - Ve a [vercel.com](https://vercel.com)
   - Conecta tu cuenta de GitHub
   - Importa este repositorio
   - Selecciona la carpeta `frontend` como directorio raíz

2. **Configurar variables de entorno en Vercel:**
   - En el dashboard de Vercel, ve a tu proyecto
   - Settings → Environment Variables
   - Agrega: `REACT_APP_API_URL` = `https://tu-backend-url.com`

3. **Deploy:**
   - Vercel detectará automáticamente que es un proyecto React
   - El build se ejecutará automáticamente
   - ¡Tu app estará lista!

### Deploy manual con Vercel CLI

```bash
# Instalar Vercel CLI
npm i -g vercel

# Desde el directorio frontend
cd frontend
vercel

# Para producción
vercel --prod
```

## 🔧 Scripts disponibles

- `npm start`: Servidor de desarrollo
- `npm run build`: Construir para producción
- `npm test`: Ejecutar tests
- `npm run eject`: Eject configuración

## 📁 Estructura del proyecto

```
frontend/
├── public/
├── src/
├── package.json
├── vercel.json         # Configuración de Vercel
├── .env.example        # Ejemplo de variables de entorno
└── README.md
```

## ⚙️ Configuración

- **vercel.json**: Configuración de rutas y variables para Vercel
- **.env**: Variables de entorno locales
- SPA routing configurado para React Router

## 🌐 URLs

- **Desarrollo**: http://localhost:3000
- **Producción**: https://tu-proyecto.vercel.app