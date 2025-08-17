// Configuración para diferentes entornos
const getApiBaseUrl = () => {
  // Usar variable de entorno si está definida
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // En producción (Docker), usar URL relativa
  if (import.meta.env.PROD) {
    return '';
  }
  
  // En desarrollo, usar localhost:8001 para PostgreSQL
  return 'http://localhost:8001';
};

export const API_BASE_URL = getApiBaseUrl();
