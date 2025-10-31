// ========================================
// CONFIGURAÇÕES DE PRODUÇÃO
// ========================================

// URL da API - Será atualizada após deploy do backend
const API_CONFIG = {
  baseURL: 'https://sua-api-railway.up.railway.app', // ⚠️ ATUALIZAR após deploy
  apiEndpoint: '/api',
  authEndpoint: '/auth',
  timeout: 10000,
  retryAttempts: 3,
  auth: {
    tokenKey: 'authToken',
    userKey: 'currentUser',
    tokenHeader: 'Authorization',
    tokenPrefix: 'Bearer ',
    refreshThreshold: 5 * 60 * 1000 // 5 minutos
  }
};

// Configurações de UI
const UI_CONFIG = {
  animationDuration: 300,
  toastDuration: 4000,
  loadingDelay: 1000,
  defaultPageSize: 20,
  maxFileSize: 5 * 1024 * 1024, // 5MB
  supportedImageFormats: ['jpg', 'jpeg', 'png', 'gif', 'webp'],
  dateFormat: 'DD/MM/YYYY',
  currency: 'BRL'
};

// Configurações de temas
const THEME_CONFIG = {
  defaultTheme: 'light',
  defaultColorMode: 'default',
  storageKeys: {
    theme: 'gestao_indicadores_theme',
    colorMode: 'gestao_indicadores_color_mode',
    userPreferences: 'gestao_indicadores_user_prefs'
  }
};

// Mensagens do sistema
const MESSAGES = {
  loading: 'Carregando...',
  saving: 'Salvando...',
  success: 'Operação realizada com sucesso!',
  error: 'Ocorreu um erro. Tente novamente.',
  noData: 'Nenhum dado encontrado.',
  invalidData: 'Dados inválidos fornecidos.',
  networkError: 'Erro de conexão. Verifique sua internet.',
  unauthorized: 'Acesso não autorizado.',
  sessionExpired: 'Sessão expirada. Faça login novamente.',
  confirmDelete: 'Tem certeza que deseja excluir este item?',
  unsavedChanges: 'Você tem alterações não salvas. Deseja continuar?',
  
  // Mensagens específicas do sistema
  unidadeRequired: 'Selecione uma unidade.',
  periodoRequired: 'Informe o período (mês e ano).',
  indicadorRequired: 'Preencha os indicadores ou marque "Não se aplica".',
  imageUrlInvalid: 'URL da imagem inválida.'
};

// Configurações de validação
const VALIDATION_CONFIG = {
  email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  phone: /^\(\d{2}\)\s\d{4,5}-\d{4}$/,
  url: /^https?:\/\/.+\..+/,
  numericOnly: /^\d+$/,
  alphanumericOnly: /^[a-zA-Z0-9]+$/,
  
  // Limites
  minYear: 2020,
  maxYear: new Date().getFullYear() + 5,
  minMonth: 1,
  maxMonth: 12,
  maxIndicadorNome: 100,
  maxDescricao: 500,
  maxNumerador: 999999,
  maxDenominador: 999999
};

// Permissões por role
const PERMISSIONS = {
  roles: {
    operador: {
      canViewDashboard: true,
      canCreateLancamento: true,
      canEditOwnLancamento: true,
      canViewOwnUnidade: true,
      canExportData: false,
      canManageUsers: false,
      canManageUnidades: false,
      canViewAllUnidades: false
    },
    gestor: {
      canViewDashboard: true,
      canCreateLancamento: true,
      canEditOwnLancamento: true,
      canEditAllLancamentos: true,
      canViewOwnUnidade: true,
      canViewAllUnidades: true,
      canExportData: true,
      canManageUsers: false,
      canManageUnidades: false,
      canViewReports: true
    },
    admin: {
      canViewDashboard: true,
      canCreateLancamento: true,
      canEditOwnLancamento: true,
      canEditAllLancamentos: true,
      canViewOwnUnidade: true,
      canViewAllUnidades: true,
      canExportData: true,
      canManageUsers: true,
      canManageUnidades: true,
      canViewReports: true,
      canManageSystem: true
    }
  }
};

// Meses do ano
const MONTHS = [
  { value: 1, label: 'Janeiro', short: 'Jan' },
  { value: 2, label: 'Fevereiro', short: 'Fev' },
  { value: 3, label: 'Março', short: 'Mar' },
  { value: 4, label: 'Abril', short: 'Abr' },
  { value: 5, label: 'Maio', short: 'Mai' },
  { value: 6, label: 'Junho', short: 'Jun' },
  { value: 7, label: 'Julho', short: 'Jul' },
  { value: 8, label: 'Agosto', short: 'Ago' },
  { value: 9, label: 'Setembro', short: 'Set' },
  { value: 10, label: 'Outubro', short: 'Out' },
  { value: 11, label: 'Novembro', short: 'Nov' },
  { value: 12, label: 'Dezembro', short: 'Dez' }
];

// Utilitários de API
const ApiUtils = {
  /**
   * Faz requisição autenticada para a API
   */
  async request(endpoint, options = {}) {
    const token = localStorage.getItem(API_CONFIG.auth.tokenKey);
    const defaultHeaders = {
      'Content-Type': 'application/json'
    };

    if (token) {
      defaultHeaders[API_CONFIG.auth.tokenHeader] = 
        API_CONFIG.auth.tokenPrefix + token;
    }

    const config = {
      method: options.method || 'GET',
      headers: {
        ...defaultHeaders,
        ...options.headers
      },
      ...options
    };

    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body);
    }

    // Determinar URL base correta baseada no endpoint
    let baseUrl = API_CONFIG.baseURL;
    if (endpoint.startsWith('/auth/')) {
      // Endpoints de autenticação usam /auth
      baseUrl = API_CONFIG.baseURL;
    } else if (endpoint.startsWith('/api/')) {
      // Endpoints da API usam /api
      baseUrl = API_CONFIG.baseURL;
    } else {
      // Caso não tenha prefixo, assumir que é API
      endpoint = `/api${endpoint}`;
    }

    try {
      const response = await fetch(`${baseUrl}${endpoint}`, config);
      
      // Verificar se o token expirou
      if (response.status === 401) {
        localStorage.removeItem(API_CONFIG.auth.tokenKey);
        localStorage.removeItem(API_CONFIG.auth.userKey);
        
        if (window.authManager) {
          window.authManager.showLogin();
        }
        
        throw new Error('Token expirado. Faça login novamente.');
      }

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || `Erro HTTP: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error('Erro na requisição API:', error);
      throw error;
    }
  },

  /**
   * GET request
   */
  async get(endpoint, params = {}) {
    const urlParams = new URLSearchParams(params);
    const url = urlParams.toString() ? `${endpoint}?${urlParams}` : endpoint;
    return this.request(url);
  },

  /**
   * POST request
   */
  async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: data
    });
  },

  /**
   * PUT request
   */
  async put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: data
    });
  },

  /**
   * DELETE request
   */
  async delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE'
    });
  }
};

// Exporta as configurações para uso global
window.APP_CONFIG = {
  API_CONFIG,
  UI_CONFIG,
  THEME_CONFIG,
  MESSAGES,
  VALIDATION_CONFIG,
  PERMISSIONS,
  MONTHS,
  ApiUtils
};

// Log de inicialização
console.log('🏥 Gestão de Indicadores Hospitalares - Configurações carregadas');
console.log('📊 Versão:', '1.0.0');
console.log('🔧 Ambiente:', 'Produção');