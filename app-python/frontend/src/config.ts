// Configuración para diferentes entornos
const getApiBaseUrl = () => {
  // Si VITE_API_URL está definida, usarla
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // En producción (Docker), usar URL relativa
  if (import.meta.env.PROD) {
    return '';
  }
  
  // En desarrollo, usar localhost:8000
  return 'http://localhost:8000';
};

export const API_BASE_URL = getApiBaseUrl();
