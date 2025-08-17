// Configuración para diferentes entornos
const getApiBaseUrl = () => {
  // Siempre usar variable de entorno si está definida
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // Fallback para PostgreSQL
  return 'http://localhost:8001';
};

export const API_BASE_URL = getApiBaseUrl();
