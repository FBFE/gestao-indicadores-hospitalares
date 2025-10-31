// ========================================
// APLICAÇÃO PRINCIPAL - GESTÃO DE INDICADORES HOSPITALARES
// ========================================

class GestaoIndicadoresApp {
  constructor() {
    this.userProfile = null;
    this.dicionarioIndicadores = [];
    this.listaUnidades = [];
    this.cache = new Map();
    this.modalInstances = {};
    this.currentPage = 'dashboard';
    this.loadingScreen = null;
    this.authManager = null;
    
    // Binding dos métodos
    this.init = this.init.bind(this);
    this.carregarDadosIniciais = this.carregarDadosIniciais.bind(this);
    this.navegarPara = this.navegarPara.bind(this);
  }

  // ========================================
  // INICIALIZAÇÃO
  // ========================================
  
  async init() {
    try {
      this.log('info', 'Iniciando aplicação...');
      
      // Aguarda autenticação - se não há usuário logado, para aqui
      if (!window.authManager || !window.authManager.currentUser) {
        this.log('info', 'Aguardando autenticação...');
        return;
      }
      
      this.authManager = window.authManager;
      this.userProfile = this.authManager.currentUser;
      
      // Valida configurações
      if (!window.APP_CONFIG.ConfigUtils.validate()) {
        throw new Error('Configurações inválidas');
      }
      
      // Inicializa componentes Materialize
      this.initMaterializeComponents();
      
      // Configura event listeners
      this.setupEventListeners();
      
      // Carrega preferências do usuário
      this.loadUserPreferences();
      
      // Inicializa AOS (Animate On Scroll)
      if (typeof AOS !== 'undefined') {
        AOS.init({
          duration: 600,
          easing: 'ease-in-out',
          once: true,
          offset: 50
        });
      }
      
      // Carrega dados iniciais
      await this.carregarDadosIniciais();
      
      // Remove tela de loading
      setTimeout(() => {
        this.hideLoadingScreen();
      }, window.APP_CONFIG.UI_CONFIG.loadingDelay);
      
      this.log('info', 'Aplicação inicializada com sucesso');
      
    } catch (error) {
      this.log('error', 'Erro na inicialização:', error);
      this.showError('Erro ao inicializar a aplicação. Tente recarregar a página.');
      this.hideLoadingScreen();
    }
  }
  
  setupLoadingScreen() {
    this.loadingScreen = document.getElementById('loading-screen');
    
    // Anima a barra de progresso
    const progressBar = document.querySelector('.loading-progress');
    if (progressBar) {
      setTimeout(() => {
        progressBar.style.width = '100%';
      }, 500);
    }
  }
  
  hideLoadingScreen() {
    if (this.loadingScreen) {
      this.loadingScreen.classList.add('hidden');
      setTimeout(() => {
        this.loadingScreen.style.display = 'none';
        document.getElementById('app-content').style.display = 'block';
        this.navegarPara('dashboard');
      }, 500);
    }
  }
  
  initMaterializeComponents() {
    // Sidenav
    M.Sidenav.init(document.querySelectorAll('.sidenav'), {
      edge: 'left',
      draggable: true
    });
    
    // Select
    M.FormSelect.init(document.querySelectorAll('select'));
    
    // Modais
    this.modalInstances.info = M.Modal.init(document.getElementById('infoModal'));
    this.modalInstances.dashboard = M.Modal.init(document.getElementById('dashboardDetailModal'));
    
    // Tooltip
    M.Tooltip.init(document.querySelectorAll('.tooltipped'));
    
    // Collapsible
    M.Collapsible.init(document.querySelectorAll('.collapsible'));
  }
  
  setupEventListeners() {
    // Tema escuro
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const darkModeToggleMobile = document.getElementById('dark-mode-toggle-mobile');
    
    if (darkModeToggle) {
      darkModeToggle.addEventListener('change', (e) => this.toggleDarkMode(e.target.checked));
    }
    
    if (darkModeToggleMobile) {
      darkModeToggleMobile.addEventListener('change', (e) => this.toggleDarkMode(e.target.checked));
    }
    
    // Modo daltonismo
    const colorblindSelect = document.getElementById('colorblind-mode');
    const colorblindSelectMobile = document.getElementById('colorblind-mode-mobile');
    
    if (colorblindSelect) {
      colorblindSelect.addEventListener('change', (e) => this.changeColorblindMode(e.target.value));
    }
    
    if (colorblindSelectMobile) {
      colorblindSelectMobile.addEventListener('change', (e) => this.changeColorblindMode(e.target.value));
    }
    
    // Teclas de atalho
    document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));
    
    // Online/Offline
    window.addEventListener('online', () => this.handleConnectionChange(true));
    window.addEventListener('offline', () => this.handleConnectionChange(false));
    
    // Beforeunload
    window.addEventListener('beforeunload', (e) => this.handleBeforeUnload(e));
  }
  
  // ========================================
  // GERENCIAMENTO DE DADOS
  // ========================================
  
  async carregarDadosIniciais() {
    const promises = [
      this.getUnidades(),
      this.getIndicadoresDicionario()
    ];
    
    try {
      const [unidades, indicadores] = await Promise.allSettled(promises);
      
      if (unidades.status === 'fulfilled') {
        this.onUnidadesSuccess(unidades.value);
      } else {
        this.log('error', 'Erro ao carregar unidades:', unidades.reason);
      }
      
      if (indicadores.status === 'fulfilled') {
        this.onDicionarioSuccess(indicadores.value);
      } else {
        this.log('error', 'Erro ao carregar indicadores:', indicadores.reason);
      }
      
      // Atualizar interface com dados do usuário
      this.updateUserInfo();
      this.updateUIForRole();
      
    } catch (error) {
      this.log('error', 'Erro geral no carregamento:', error);
      this.showError('Erro ao carregar dados iniciais');
    }
  }
  
  // ========================================
  // API CALLS
  // ========================================
  
  async makeApiCall(endpoint, options = {}) {
    const { method = 'GET', body = null, headers = {}, timeout = window.APP_CONFIG.API_CONFIG.timeout } = options;
    
    const config = {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...headers
      },
      signal: AbortSignal.timeout(timeout)
    };
    
    if (body) {
      config.body = JSON.stringify(body);
    }
    
    try {
      const response = await fetch(`${window.APP_CONFIG.API_CONFIG.baseURL}${endpoint}`, config);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      this.log('error', `API Error (${endpoint}):`, error);
      throw error;
    }
  }
  
  async getUserProfile() {
    const cacheKey = window.APP_CONFIG.CACHE_CONFIG.keys.userProfile;
    const cached = this.getFromCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      const profile = await this.makeApiCall('/auth/profile');
      this.setCache(cacheKey, profile, window.APP_CONFIG.CACHE_CONFIG.duration.userProfile);
      return profile;
    } catch (error) {
      // Fallback para desenvolvimento
      return {
        email: 'admin@hospital.com',
        nome: 'Administrador',
        perfil: 'admin'
      };
    }
  }
  
  async getUnidades() {
    const cacheKey = window.APP_CONFIG.CACHE_CONFIG.keys.unidades;
    const cached = this.getFromCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      const unidades = await window.APP_CONFIG.ApiUtils.get('/unidades');
      this.setCache(cacheKey, unidades, window.APP_CONFIG.CACHE_CONFIG.duration.unidades);
      return unidades;
    } catch (error) {
      this.log('error', 'Erro ao buscar unidades:', error);
      // Fallback para desenvolvimento
      return [
        { id: '1', nome: 'UTI Adulto', foto_url: null },
        { id: '2', nome: 'UTI Pediátrica', foto_url: null },
        { id: '3', nome: 'Emergência', foto_url: null }
      ];
    }
  }
  
  async getIndicadoresDicionario() {
    const cacheKey = window.APP_CONFIG.CACHE_CONFIG.keys.indicadores;
    const cached = this.getFromCache(cacheKey);
    
    if (cached) {
      return cached;
    }
    
    try {
      const indicadores = await window.APP_CONFIG.ApiUtils.get('/indicadores/dicionario');
      this.setCache(cacheKey, indicadores, window.APP_CONFIG.CACHE_CONFIG.duration.indicadores);
      return indicadores;
    } catch (error) {
      this.log('error', 'Erro ao buscar indicadores:', error);
      // Fallback para desenvolvimento
      return [
        {
          nome: 'Taxa de Mortalidade',
          descricao: 'Percentual de óbitos em relação ao total de internações',
          label_numerador: 'Número de óbitos',
          label_denominador: 'Total de internações'
        },
        {
          nome: 'Taxa de Infecção Hospitalar',
          descricao: 'Percentual de infecções hospitalares',
          label_numerador: 'Casos de infecção',
          label_denominador: 'Total de pacientes'
        }
      ];
    }
  }
  
  // ========================================
  // CALLBACKS DE SUCESSO
  // ========================================
  
  onProfileSuccess(profile) {
    if (profile.error) {
      this.showError(`Erro ao buscar perfil: ${profile.error}`);
      return;
    }
    
    this.userProfile = profile;
    
    // Atualiza UI
    const userInfo = document.getElementById('userInfo');
    if (userInfo) {
      userInfo.innerHTML = `<i class="material-icons left">account_circle</i>${profile.nome}`;
    }
    
    const mobileUserName = document.getElementById('mobile-user-name');
    const mobileUserEmail = document.getElementById('mobile-user-email');
    
    if (mobileUserName) mobileUserName.textContent = profile.nome;
    if (mobileUserEmail) mobileUserEmail.textContent = profile.email;
    
    // Mostra/esconde links de admin
    const adminLinks = document.querySelectorAll('.admin-link');
    if (profile.perfil === 'admin') {
      adminLinks.forEach(el => el.style.display = 'list-item');
    }
    
    this.log('info', 'Perfil carregado:', profile);
  }

  // ========================================
  // CONTROLE DE ACESSO
  // ========================================

  hasRole(requiredRole) {
    if (!this.userProfile) return false;
    
    const userRole = this.userProfile.role;
    const roleHierarchy = {
      'operador': 1,
      'gestor': 2,
      'admin': 3
    };
    
    return roleHierarchy[userRole] >= roleHierarchy[requiredRole];
  }

  canAccessUnit(unidade) {
    if (!this.userProfile) return false;
    
    const { role, unidade: userUnit } = this.userProfile;
    
    // Gestores e admins acessam todas as unidades
    if (['gestor', 'admin'].includes(role)) {
      return true;
    }
    
    // Operadores só acessam sua unidade
    return userUnit === unidade;
  }

  filterDataByUnit(data) {
    if (!this.userProfile) return data;
    
    const { role, unidade: userUnit } = this.userProfile;
    
    // Gestores e admins veem todos os dados
    if (['gestor', 'admin'].includes(role)) {
      return data;
    }
    
    // Operadores veem apenas dados de sua unidade
    return data.filter(item => item.unidade === userUnit);
  }

  updateUIForRole() {
    if (!this.userProfile) return;
    
    const { role } = this.userProfile;
    
    // Elementos apenas para admins
    const adminElements = document.querySelectorAll('.admin-only');
    adminElements.forEach(el => {
      el.style.display = role === 'admin' ? 'block' : 'none';
    });
    
    // Elementos para gestores e admins
    const gestorElements = document.querySelectorAll('.gestor-only');
    gestorElements.forEach(el => {
      el.style.display = ['gestor', 'admin'].includes(role) ? 'block' : 'none';
    });
    
    // Links de navegação
    const adminLinks = document.querySelectorAll('.admin-link');
    adminLinks.forEach(el => {
      el.style.display = role === 'admin' ? 'list-item' : 'none';
    });
  }

  updateUserInfo() {
    if (!this.userProfile) return;
    
    const { nome, role, unidade } = this.userProfile;
    
    // Atualizar elementos com nome do usuário
    const userNameElements = document.querySelectorAll('.user-name');
    userNameElements.forEach(el => el.textContent = nome);
    
    // Atualizar role
    const userRoleElements = document.querySelectorAll('.user-role');
    const roleNames = {
      'operador': 'Operador',
      'gestor': 'Gestor',
      'admin': 'Administrador'
    };
    userRoleElements.forEach(el => el.textContent = roleNames[role] || role);
    
    // Atualizar unidade
    const userUnitElements = document.querySelectorAll('.user-unit');
    userUnitElements.forEach(el => el.textContent = unidade);
  }
  
  onUnidadesSuccess(unidades) {
    if (unidades.error) {
      this.showError(`Erro ao buscar unidades: ${unidades.error}`);
      return;
    }
    
    this.listaUnidades = unidades;
    
    // Popula selects
    this.populateUnidadeSelects(unidades);
    
    this.log('info', 'Unidades carregadas:', unidades.length);
  }
  
  onDicionarioSuccess(indicadores) {
    if (indicadores.error) {
      this.showError(`Erro ao buscar indicadores: ${indicadores.error}`);
      return;
    }
    
    this.dicionarioIndicadores = indicadores;
    
    this.log('info', 'Indicadores carregados:', indicadores.length);
  }
  
  populateUnidadeSelects(unidades) {
    const selects = [
      { id: 'filtro-unidade', defaultOption: '<option value="" selected>Todas as Unidades</option>' },
      { id: 'form-unidade', defaultOption: '<option value="" disabled selected>Selecione a Unidade</option>' },
      { id: 'admin-unidade-select', defaultOption: '<option value="" disabled selected>Selecione a Unidade</option>' }
    ];
    
    selects.forEach(({ id, defaultOption }) => {
      const select = document.getElementById(id);
      if (select) {
        select.innerHTML = defaultOption;
        
        unidades.forEach(unidade => {
          const option = document.createElement('option');
          option.value = unidade.id;
          option.textContent = unidade.nome;
          select.appendChild(option);
        });
      }
    });
    
    // Reinicializa materialize selects
    M.FormSelect.init(document.querySelectorAll('select'));
  }
  
  // ========================================
  // NAVEGAÇÃO
  // ========================================
  
  navegarPara(pageId) {
    // Remove active de todas as páginas
    document.querySelectorAll('.page').forEach(page => {
      page.classList.remove('active');
    });
    
    // Ativa a página atual
    const targetPage = document.getElementById(`page-${pageId}`);
    if (targetPage) {
      targetPage.classList.add('active');
      
      // Anima entrada
      targetPage.style.animation = 'fadeInUp 0.6s ease-out';
      
      // Atualiza título da página
      this.updatePageTitle(pageId);
      
      // Executa ações específicas da página
      this.handlePageSpecificActions(pageId);
    }
    
    this.currentPage = pageId;
    
    // Log de navegação
    this.log('info', `Navegando para: ${pageId}`);
  }
  
  updatePageTitle(pageId) {
    const titles = window.APP_CONFIG.MESSAGES;
    const pageTitle = titles[pageId] || 'Gestão de Indicadores Hospitalares';
    document.title = pageTitle;
  }
  
  handlePageSpecificActions(pageId) {
    switch (pageId) {
      case 'dashboard':
        if (typeof window.dashboardManager !== 'undefined') {
          window.dashboardManager.init();
        }
        break;
      case 'lancamento':
        if (typeof window.lancamentoManager !== 'undefined') {
          window.lancamentoManager.init();
        }
        break;
      case 'adminUnidades':
        if (typeof window.adminManager !== 'undefined') {
          window.adminManager.initUnidades();
        }
        break;
      case 'adminUsuarios':
        if (typeof window.adminManager !== 'undefined') {
          window.adminManager.initUsuarios();
        }
        break;
    }
  }
  
  fecharSidenav() {
    const sidenavInstance = M.Sidenav.getInstance(document.getElementById('mobile-nav'));
    if (sidenavInstance) {
      sidenavInstance.close();
    }
  }
  
  // ========================================
  // GERENCIAMENTO DE TEMA
  // ========================================
  
  toggleDarkMode(isDark) {
    const body = document.body;
    const toggleDesktop = document.getElementById('dark-mode-toggle');
    const toggleMobile = document.getElementById('dark-mode-toggle-mobile');
    
    if (isDark) {
      body.classList.add('dark-mode');
      localStorage.setItem(window.APP_CONFIG.THEME_CONFIG.storageKeys.theme, 'dark');
      if (toggleDesktop) toggleDesktop.checked = true;
      if (toggleMobile) toggleMobile.checked = true;
    } else {
      body.classList.remove('dark-mode');
      localStorage.setItem(window.APP_CONFIG.THEME_CONFIG.storageKeys.theme, 'light');
      if (toggleDesktop) toggleDesktop.checked = false;
      if (toggleMobile) toggleMobile.checked = false;
    }
    
    this.log('info', `Tema alterado para: ${isDark ? 'escuro' : 'claro'}`);
  }
  
  changeColorblindMode(mode) {
    const body = document.body;
    body.classList.remove('colorblind-rg', 'colorblind-by');
    
    if (mode === 'colorblind-rg' || mode === 'colorblind-by') {
      body.classList.add(mode);
      localStorage.setItem(window.APP_CONFIG.THEME_CONFIG.storageKeys.colorMode, mode);
    } else {
      localStorage.setItem(window.APP_CONFIG.THEME_CONFIG.storageKeys.colorMode, 'default');
    }
    
    // Sincroniza selects
    const selects = ['colorblind-mode', 'colorblind-mode-mobile'];
    selects.forEach(id => {
      const select = document.getElementById(id);
      if (select) {
        select.value = mode;
      }
    });
    
    M.FormSelect.init(document.querySelectorAll('#colorblind-mode, #colorblind-mode-mobile'));
    
    this.log('info', `Modo de cor alterado para: ${mode}`);
  }
  
  loadUserPreferences() {
    const savedTheme = localStorage.getItem(window.APP_CONFIG.THEME_CONFIG.storageKeys.theme);
    const savedColorMode = localStorage.getItem(window.APP_CONFIG.THEME_CONFIG.storageKeys.colorMode);
    
    if (savedTheme === 'dark') {
      this.toggleDarkMode(true);
    }
    
    if (savedColorMode) {
      this.changeColorblindMode(savedColorMode);
    }
  }
  
  // ========================================
  // CACHE
  // ========================================
  
  setCache(key, data, duration) {
    if (!window.APP_CONFIG.CACHE_CONFIG.enabled) return;
    
    const expiry = Date.now() + duration;
    this.cache.set(key, { data, expiry });
  }
  
  getFromCache(key) {
    if (!window.APP_CONFIG.CACHE_CONFIG.enabled) return null;
    
    const cached = this.cache.get(key);
    
    if (!cached) return null;
    
    if (Date.now() > cached.expiry) {
      this.cache.delete(key);
      return null;
    }
    
    return cached.data;
  }
  
  clearCache() {
    this.cache.clear();
    this.log('info', 'Cache limpo');
  }
  
  // ========================================
  // UTILIDADES
  // ========================================
  
  showError(message) {
    M.toast({
      html: `<i class="material-icons left">error</i>${message}`,
      classes: 'red darken-2',
      displayLength: window.APP_CONFIG.UI_CONFIG.toastDuration
    });
  }
  
  showSuccess(message) {
    M.toast({
      html: `<i class="material-icons left">check_circle</i>${message}`,
      classes: 'green darken-1',
      displayLength: window.APP_CONFIG.UI_CONFIG.toastDuration
    });
  }
  
  showInfo(message) {
    M.toast({
      html: `<i class="material-icons left">info</i>${message}`,
      classes: 'blue darken-1',
      displayLength: window.APP_CONFIG.UI_CONFIG.toastDuration
    });
  }
  
  log(level, message, ...args) {
    if (!window.APP_CONFIG.LOG_CONFIG.enabled) return;
    
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
    
    switch (level) {
      case 'debug':
        console.debug(logMessage, ...args);
        break;
      case 'info':
        console.info(logMessage, ...args);
        break;
      case 'warn':
        console.warn(logMessage, ...args);
        break;
      case 'error':
        console.error(logMessage, ...args);
        break;
      default:
        console.log(logMessage, ...args);
    }
  }
  
  handleKeyboardShortcuts(e) {
    // Ctrl/Cmd + K para buscar
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      // Implementar busca global
    }
    
    // Ctrl/Cmd + D para dashboard
    if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
      e.preventDefault();
      this.navegarPara('dashboard');
    }
    
    // Ctrl/Cmd + L para lançamento
    if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
      e.preventDefault();
      this.navegarPara('lancamento');
    }
  }
  
  handleConnectionChange(isOnline) {
    if (isOnline) {
      this.showInfo('Conexão restaurada');
      this.clearCache(); // Recarrega dados
      this.carregarDadosIniciais();
    } else {
      this.showError('Sem conexão com a internet');
    }
  }
  
  handleBeforeUnload(e) {
    // Verifica se há mudanças não salvas
    if (this.hasUnsavedChanges()) {
      e.preventDefault();
      return e.returnValue = window.APP_CONFIG.MESSAGES.unsavedChanges;
    }
  }
  
  hasUnsavedChanges() {
    // Implementar lógica para detectar mudanças não salvas
    return false;
  }
}

// ========================================
// INICIALIZAÇÃO GLOBAL
// ========================================

// Instância global da aplicação
window.app = new GestaoIndicadoresApp();

// Event listener para inicialização
document.addEventListener('DOMContentLoaded', () => {
  window.app.init();
});

// Funções globais para compatibilidade
window.navegarPara = (pageId) => window.app.navegarPara(pageId);
window.fecharSidenav = () => window.app.fecharSidenav();