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
        ? 'https://SEU-BACKEND-RAILWAY.up.railway.app'  // ⚠️ ATUALIZAR COM SUA URL DO RAILWAY
        : 'http://localhost:5000'  // Desenvolvimento local
};

// Log para debug
console.log('🔗 API URL:', API_CONFIG.baseURL);

// Para debug - mostrar no console qual config está sendo usada
if (isProduction) {
    console.log('📡 Usando configuração de PRODUÇÃO');
    console.log('🚨 LEMBRE-SE: Atualize a URL do Railway no arquivo config-auto.js');
} else {
    console.log('💻 Usando configuração de DESENVOLVIMENTO');
    console.log('🔧 Certifique-se que o servidor local está rodando na porta 5000');
}

// Exportar para uso global
window.API_CONFIG = API_CONFIG;