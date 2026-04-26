/**
 * Configuración de URLs del Sistema Carrocería Alvarado
 * 
 * INSTRUCCIONES PARA DESPLIEGUE CON NGROK:
 * 1. Para desarrollo local, mantén API_BASE_URL como está
 * 2. Para despliegue con ngrok, cambia API_BASE_URL a tu URL de ngrok del backend
 *    Ejemplo: const API_BASE_URL = 'https://abc123.ngrok-free.app';
 */

// URL del Backend API
const API_BASE_URL = 'https://carroceriaalvarado.fly.dev';

// Exportar para uso en otros archivos
window.CONFIG = {
    API_BASE_URL: API_BASE_URL
};

console.log('Configuración cargada. API URL:', API_BASE_URL);
