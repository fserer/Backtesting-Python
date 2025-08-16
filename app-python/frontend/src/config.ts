// Configuración para diferentes entornos
const getApiBaseUrl = () => {
  // En producción (Docker), usar URL relativa
  if (import.meta.env.PROD) {
    return '';
  }
  
  // En desarrollo, usar localhost:8000
  return 'http://localhost:8000';
};

export const API_BASE_URL = getApiBaseUrl();
