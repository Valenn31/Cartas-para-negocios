import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import App from './App';
import Admin from './Admin';

// Componente para redireccionar /admin al Django
function AdminRedirect() {
  useEffect(() => {
    window.location.href = 'https://cartas-para-negocios-production.up.railway.app/admin/web/login/';
  }, []);
  return null;
}

function AppRouter() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/admin" element={<AdminRedirect />} />
        <Route path="/admin/:restaurant_slug/editar" element={<Admin />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default AppRouter;
