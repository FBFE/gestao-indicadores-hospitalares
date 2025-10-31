// 🔧 CONFIGURAÇÃO DE AMBIENTE
// Este arquivo detecta automaticamente se está em produção ou desenvolvimento

// Detectar ambiente
const isProduction = window.location.hostname !== 'localhost' && 
                     window.location.hostname !== '127.0.0.1' && 
                     window.location.hostname !== '';

console.log('🌍 Ambiente detectado:', isProduction ? 'PRODUÇÃO' : 'DESENVOLVIMENTO');

// Configuração baseada no ambiente
const API_CONFIG = {
    baseURL: isProduction 
        ? 'https://gestao-indicadores-hospitalares-production.up.railway.app'  // ✅ URL DO RAILWAY CONFIGURADA
        : 'http://localhost:5000'  // Desenvolvimento local
};

// Log para debug
console.log('🔗 API URL:', API_CONFIG.baseURL);

// Para debug - mostrar no console qual config está sendo usada
if (isProduction) {
    console.log('📡 Usando configuração de PRODUÇÃO');
    console.log('� API Railway: https://gestao-indicadores-hospitalares-production.up.railway.app');
} else {
    console.log('💻 Usando configuração de DESENVOLVIMENTO');
    console.log('🔧 Certifique-se que o servidor local está rodando na porta 5000');
}

// ApiUtils para fazer requisições
const ApiUtils = {
    async get(endpoint) {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_CONFIG.baseURL}${endpoint}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': `Bearer ${token}` })
            }
        });
        return await response.json();
    },

    async post(endpoint, data) {
        console.log(`📡 POST ${API_CONFIG.baseURL}${endpoint}`, data);
        
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_CONFIG.baseURL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': `Bearer ${token}` })
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        console.log(`📡 Response ${response.status}:`, result);
        
        if (!response.ok) {
            throw new Error(result.message || `HTTP ${response.status}`);
        }
        
        return result;
    },

    async put(endpoint, data) {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_CONFIG.baseURL}${endpoint}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': `Bearer ${token}` })
            },
            body: JSON.stringify(data)
        });
        return await response.json();
    },

    async delete(endpoint) {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_CONFIG.baseURL}${endpoint}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': `Bearer ${token}` })
            }
        });
        return await response.json();
    }
};

// Configuração completa com ApiUtils
const APP_CONFIG = {
    baseURL: API_CONFIG.baseURL,
    ApiUtils
};

// Exportar para uso global
window.API_CONFIG = API_CONFIG;
window.APP_CONFIG = APP_CONFIG;