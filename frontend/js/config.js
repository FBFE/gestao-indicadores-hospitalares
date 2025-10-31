// ========================================
// CONFIGURAÇÕES GLOBAIS DA APLICAÇÃO
// ========================================

// URL da API - Configure conforme seu ambiente
const API_CONFIG = {
  baseURL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000' 
    : 'https://sua-api.netlify.app',
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

// Configurações do Google Sheets
const GOOGLE_SHEETS_CONFIG = {
  spreadsheetId: '1RXm-9-K_1H8GZjvNjnhpBvNnDQCejDMkBUPEKF26Too',
  apiKey: null, // Será configurado via variáveis de ambiente
  sheets: {
    usuarios: 'Usuarios',
    unidades: 'Unidades', 
    indicadores: 'Indicadores_Dicionario',
    lancamentos: 'Lancamentos'
  }
};

// Configurações de UI
const UI_CONFIG = {
  animationDuration: 300,
  toastDuration: 4000,
  loadingDelay: 1500,
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
  imageUrlInvalid: 'URL da imagem inválida.',
  
  // Títulos das páginas
  dashboard: 'Dashboard - Visão Geral dos Indicadores',
  lancamento: 'Lançamento em Lote - Inserir Dados',
  adminUnidades: 'Administração - Gerenciar Unidades',
  adminUsuarios: 'Administração - Gerenciar Usuários'
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

// Configurações de permissões
const PERMISSIONS = {
  roles: {
    admin: {
      dashboard: true,
      lancamento: true,
      adminUnidades: true,
      adminUsuarios: true,
      deleteData: true,
      exportData: true
    },
    gestor: {
      dashboard: true,
      lancamento: true,
      adminUnidades: false,
      adminUsuarios: false,
      deleteData: false,
      exportData: true
    },
    operador: {
      dashboard: true,
      lancamento: true,
      adminUnidades: false,
      adminUsuarios: false,
      deleteData: false,
      exportData: false
    },
    visualizador: {
      dashboard: true,
      lancamento: false,
      adminUnidades: false,
      adminUsuarios: false,
      deleteData: false,
      exportData: false
    }
  }
};

// Configurações de cache
const CACHE_CONFIG = {
  enabled: true,
  duration: {
    userProfile: 5 * 60 * 1000, // 5 minutos
    unidades: 30 * 60 * 1000, // 30 minutos
    indicadores: 60 * 60 * 1000, // 1 hora
    lancamentos: 2 * 60 * 1000 // 2 minutos
  },
  keys: {
    userProfile: 'cache_user_profile',
    unidades: 'cache_unidades',
    indicadores: 'cache_indicadores',
    lancamentos: 'cache_lancamentos_'
  }
};

// Configurações de logs
const LOG_CONFIG = {
  enabled: true,
  level: 'info', // 'debug', 'info', 'warn', 'error'
  maxEntries: 1000,
  storageKey: 'gestao_indicadores_logs'
};

// Status dos indicadores
const STATUS_TYPES = {
  green: {
    color: '#28a745',
    label: 'Adequado',
    icon: 'check_circle'
  },
  yellow: {
    color: '#ffc107',
    label: 'Atenção',
    icon: 'warning'
  },
  red: {
    color: '#dc3545',
    label: 'Crítico',
    icon: 'error'
  },
  gray: {
    color: '#6c757d',
    label: 'Sem dados',
    icon: 'help'
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

// Utilitários de configuração
const ConfigUtils = {
  // Obtém configuração por caminho (ex: 'api.baseURL')
  get(path, defaultValue = null) {
    const keys = path.split('.');
    let value = window;
    
    for (const key of keys) {
      if (value && typeof value === 'object' && key in value) {
        value = value[key];
      } else {
        return defaultValue;
      }
    }
    
    return value !== undefined ? value : defaultValue;
  },
  
  // Verifica se uma permissão está habilitada para o role
  hasPermission(role, permission) {
    return PERMISSIONS.roles[role]?.[permission] || false;
  },
  
  // Obtém label do mês
  getMonthLabel(monthNumber, short = false) {
    const month = MONTHS.find(m => m.value === parseInt(monthNumber));
    return month ? (short ? month.short : month.label) : '';
  },
  
  // Valida configurações no startup
  validate() {
    const errors = [];
    
    if (!API_CONFIG.baseURL) {
      errors.push('URL da API não configurada');
    }
    
    if (!GOOGLE_SHEETS_CONFIG.spreadsheetId) {
      errors.push('ID da planilha Google Sheets não configurado');
    }
    
    if (errors.length > 0) {
      console.error('Erros de configuração:', errors);
      return false;
    }
    
    return true;
  },
  
  // Obtém configurações do usuário do localStorage
  getUserPreferences() {
    try {
      const prefs = localStorage.getItem(THEME_CONFIG.storageKeys.userPreferences);
      return prefs ? JSON.parse(prefs) : {};
    } catch (error) {
      console.error('Erro ao carregar preferências:', error);
      return {};
    }
  },
  
  // Salva configurações do usuário no localStorage
  saveUserPreferences(preferences) {
    try {
      const currentPrefs = this.getUserPreferences();
      const newPrefs = { ...currentPrefs, ...preferences };
      localStorage.setItem(
        THEME_CONFIG.storageKeys.userPreferences, 
        JSON.stringify(newPrefs)
      );
      return true;
    } catch (error) {
      console.error('Erro ao salvar preferências:', error);
      return false;
    }
  }
};

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
  GOOGLE_SHEETS_CONFIG,
  UI_CONFIG,
  THEME_CONFIG,
  MESSAGES,
  VALIDATION_CONFIG,
  PERMISSIONS,
  CACHE_CONFIG,
  LOG_CONFIG,
  STATUS_TYPES,
  MONTHS,
  ConfigUtils,
  ApiUtils
};

// Log de inicialização
console.log('🏥 Gestão de Indicadores Hospitalares - Configurações carregadas');
console.log('📊 Versão:', '1.0.0');
console.log('🔧 Ambiente:', window.location.hostname === 'localhost' ? 'Desenvolvimento' : 'Produção');