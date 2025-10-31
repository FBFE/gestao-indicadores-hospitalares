/**
 * Sistema de Autenticação
 * Gestão de Indicadores Hospitalares
 */

class AuthManager {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    init() {
        // Aguardar o DOM estar pronto
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initAuth());
        } else {
            this.initAuth();
        }
    }

    initAuth() {
        try {
            console.log('Inicializando autenticação...');
            
            // Configurar eventos dos formulários
            this.setupEventListeners();

            // Verificar se há usuário logado no localStorage
            const savedUser = localStorage.getItem('currentUser');
            if (savedUser) {
                try {
                    this.currentUser = JSON.parse(savedUser);
                    console.log('Usuário encontrado no localStorage:', this.currentUser.nome);
                    this.showMainApp();
                } catch (error) {
                    console.error('Erro ao carregar usuário salvo:', error);
                    localStorage.removeItem('currentUser');
                    localStorage.removeItem('authToken');
                    this.showLogin();
                }
            } else {
                console.log('Nenhum usuário logado, mostrando login');
                this.showLogin();
            }
        } catch (error) {
            console.error('Erro na inicialização da autenticação:', error);
            this.showLogin();
        }
    }

    setupEventListeners() {
        try {
            // Form de login
            const loginForm = document.getElementById('login-form');
            if (loginForm) {
                loginForm.addEventListener('submit', (e) => this.handleLogin(e));
                console.log('✅ Event listener do login configurado');
            } else {
                console.warn('⚠️ Formulário de login não encontrado');
            }

            // Form de cadastro
            const cadastroForm = document.getElementById('cadastro-form');
            if (cadastroForm) {
                cadastroForm.addEventListener('submit', (e) => this.handleCadastro(e));
                console.log('✅ Event listener do cadastro configurado');
            } else {
                console.warn('⚠️ Formulário de cadastro não encontrado');
            }

            // Validação de confirmação de senha
            const confirmPassword = document.getElementById('cadastro-confirm-password');
            if (confirmPassword) {
                confirmPassword.addEventListener('blur', this.validatePasswordMatch);
                console.log('✅ Validação de senha configurada');
            }
        } catch (error) {
            console.error('Erro ao configurar event listeners:', error);
        }
    }

    async handleLogin(event) {
        event.preventDefault();
        
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        if (!this.validateEmail(email)) {
            this.showError('Email inválido');
            return;
        }

        if (!password) {
            this.showError('Senha obrigatória');
            return;
        }

        try {
            const result = await window.APP_CONFIG.ApiUtils.post('/auth/login', {
                email,
                senha: password  // Backend espera 'senha', não 'password'
            });

            if (result.token && result.user) {
                this.currentUser = result.user;
                localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
                localStorage.setItem('authToken', result.token);
                
                this.showSuccess('Login realizado com sucesso!');
                setTimeout(() => this.showMainApp(), 1500);
            } else {
                this.showError('Resposta inválida do servidor');
            }
            
        } catch (error) {
            console.error('Erro no login:', error);
            this.showError(error.message || 'Erro ao fazer login');
        }
    }

    async handleCadastro(event) {
        event.preventDefault();
        
        console.log('🔄 Iniciando processo de cadastro...');

        const formData = {
            nome: document.getElementById('cadastro-nome').value,
            email: document.getElementById('cadastro-email').value,
            senha: document.getElementById('cadastro-password').value,  // Backend espera 'senha'
            confirmPassword: document.getElementById('cadastro-confirm-password').value,
            unidade_id: parseInt(document.getElementById('cadastro-unidade').value),  // Backend espera 'unidade_id' como int
            coren: document.getElementById('cadastro-coren').value || null,
            role: 'operador' // Padrão para novos usuários
        };

        console.log('📝 Dados do formulário:', formData);

        // Validações
        if (!this.validateCadastroForm(formData)) {
            return;
        }

        try {
            // Remover confirmPassword antes de enviar para API
            const { confirmPassword, ...apiData } = formData;
            
            console.log('📡 Enviando para API:', apiData);
            
            const result = await window.APP_CONFIG.ApiUtils.post('/auth/register', apiData);
            
            console.log('✅ Resposta da API:', result);
            
            if (result.token && result.user) {
                this.showSuccess('Cadastro realizado com sucesso! Redirecionando...');
                
                // Fazer login automático após cadastro
                this.currentUser = result.user;
                localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
                localStorage.setItem('authToken', result.token);
                
                setTimeout(() => this.showMainApp(), 2000);
            } else if (result.message && result.message.includes('sucesso')) {
                this.showSuccess('Cadastro realizado com sucesso! Faça login para continuar.');
                setTimeout(() => this.mostrarLogin(), 2000);
            } else {
                this.showError(result.message || 'Erro no cadastro');
            }
            
        } catch (error) {
            console.error('❌ Erro no cadastro:', error);
            this.showError(error.message || 'Erro ao realizar cadastro');
        }
    }

    validateCadastroForm(data) {
        console.log('🔍 Validando formulário:', data);
        
        if (!data.nome.trim()) {
            this.showError('Nome é obrigatório');
            return false;
        }

        if (!this.validateEmail(data.email)) {
            this.showError('Email inválido');
            return false;
        }

        if (data.senha.length < 6) {
            this.showError('Senha deve ter pelo menos 6 caracteres');
            return false;
        }

        if (data.senha !== data.confirmPassword) {
            this.showError('Senhas não coincidem');
            return false;
        }

        if (!data.unidade_id || isNaN(data.unidade_id)) {
            this.showError('Selecione uma unidade');
            return false;
        }

        console.log('✅ Validação passou!');
        return true;
    }

    validatePasswordMatch() {
        const password = document.getElementById('cadastro-password').value;
        const confirmPassword = document.getElementById('cadastro-confirm-password').value;
        const confirmField = document.getElementById('cadastro-confirm-password');

        if (confirmPassword && password !== confirmPassword) {
            confirmField.classList.add('invalid');
            confirmField.classList.remove('valid');
        } else if (confirmPassword) {
            confirmField.classList.add('valid');
            confirmField.classList.remove('invalid');
        }
    }

    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    showLogin() {
        try {
            console.log('Exibindo tela de login...');
            
            // Esconder tela de loading
            const loadingScreen = document.getElementById('loading-screen');
            if (loadingScreen) {
                loadingScreen.style.display = 'none';
                console.log('✅ Loading screen escondido');
            }

            // Mostrar login
            const loginSection = document.getElementById('login-section');
            if (loginSection) {
                loginSection.style.display = 'block';
                console.log('✅ Tela de login exibida');
            } else {
                console.error('❌ Elemento login-section não encontrado');
            }

            // Esconder outras seções
            const cadastroSection = document.getElementById('cadastro-section');
            if (cadastroSection) {
                cadastroSection.style.display = 'none';
            }
            
            const mainApp = document.getElementById('main-app');
            if (mainApp) {
                mainApp.style.display = 'none';
            }
        } catch (error) {
            console.error('Erro ao exibir login:', error);
        }
    }

    showCadastro() {
        // Esconder tela de loading
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.style.display = 'none';
        }

        document.getElementById('login-section').style.display = 'none';
        document.getElementById('cadastro-section').style.display = 'block';
        
        const mainApp = document.getElementById('main-app');
        if (mainApp) {
            mainApp.style.display = 'none';
        }
        
        // Inicializar select do Materialize
        setTimeout(() => {
            M.FormSelect.init(document.querySelectorAll('select'));
        }, 100);
    }

    showMainApp() {
        // Esconder tela de loading
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.style.display = 'none';
        }

        document.getElementById('login-section').style.display = 'none';
        document.getElementById('cadastro-section').style.display = 'none';
        document.getElementById('main-app').style.display = 'block';
        
        // Atualizar interface baseada no usuário logado
        this.updateUserInterface();
        
        // Inicializar aplicação principal se ainda não foi inicializada
        if (!window.app) {
            // Aguardar um pouco para garantir que o DOM está pronto
            setTimeout(() => {
                window.app = new GestaoIndicadoresApp();
                window.app.init();
            }, 100);
        } else {
            // Se já existe, apenas recarregar dados
            window.app.userProfile = this.currentUser;
            window.app.carregarDadosIniciais();
        }
    }

    updateUserInterface() {
        if (!this.currentUser) return;

        // Atualizar informações completas do usuário
        this.updateUserInfo();

        // Mostrar/ocultar elementos baseado no role
        this.updateRoleBasedVisibility();

        // Configurar filtros de unidade
        this.setupUnitFilters();
    }

    updateUserInfo() {
        if (!this.currentUser) return;
        
        const { nome, role, unidade } = this.currentUser;
        
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
        
        // Inicializar dropdown do usuário
        setTimeout(() => {
            M.Dropdown.init(document.querySelectorAll('.dropdown-trigger'), {
                coverTrigger: false,
                constrainWidth: false
            });
        }, 100);
    }

    updateRoleBasedVisibility() {
        const { role } = this.currentUser;

        // Elementos apenas para gestores e admins
        const adminElements = document.querySelectorAll('.admin-only');
        const gestorElements = document.querySelectorAll('.gestor-only');

        adminElements.forEach(el => {
            el.style.display = role === 'admin' ? 'block' : 'none';
        });

        gestorElements.forEach(el => {
            el.style.display = ['gestor', 'admin'].includes(role) ? 'block' : 'none';
        });

        // Atualizar menu de navegação
        const adminNavItems = document.querySelectorAll('.nav-item.admin-only');
        adminNavItems.forEach(item => {
            item.style.display = role === 'admin' ? 'block' : 'none';
        });
    }

    setupUnitFilters() {
        const { role, unidade } = this.currentUser;

        if (role === 'operador') {
            // Operadores veem apenas sua unidade
            window.currentUnitFilter = unidade;
            window.canChangeUnit = false;
        } else {
            // Gestores e admins podem ver todas as unidades
            window.currentUnitFilter = null;
            window.canChangeUnit = true;
        }
    }

    logout() {
        this.currentUser = null;
        localStorage.removeItem('currentUser');
        localStorage.removeItem('authToken');
        this.showLogin();
        
        // Limpar dados em cache
        if (window.dashboardManager) {
            window.dashboardManager.clearCache();
        }
        
        this.showSuccess('Logout realizado com sucesso!');
    }

    getUserRole() {
        return this.currentUser ? this.currentUser.role : null;
    }

    getUserUnit() {
        return this.currentUser ? this.currentUser.unidade : null;
    }

    canAccessUnit(unidade) {
        if (!this.currentUser) return false;
        
        const { role, unidade: userUnit } = this.currentUser;
        
        if (['gestor', 'admin'].includes(role)) {
            return true; // Gestores e admins acessam todas as unidades
        }
        
        return userUnit === unidade; // Operadores só acessam sua unidade
    }

    showError(message) {
        M.toast({
            html: `<i class="material-icons left">error</i>${message}`,
            classes: 'red darken-2',
            displayLength: 4000
        });
    }

    showSuccess(message) {
        M.toast({
            html: `<i class="material-icons left">check_circle</i>${message}`,
            classes: 'green darken-2',
            displayLength: 3000
        });
    }
}

// Funções globais para navegação entre login/cadastro
function mostrarLogin() {
    if (window.authManager) {
        window.authManager.showLogin();
    }
}

function mostrarCadastro() {
    if (window.authManager) {
        window.authManager.showCadastro();
    }
}

function logout() {
    if (window.authManager) {
        window.authManager.logout();
    }
}

// A inicialização agora é controlada pelo script no HTML